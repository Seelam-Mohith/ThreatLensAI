import logging
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scapy.all import IP, IPv6, TCP, UDP, PcapReader
from werkzeug.utils import secure_filename


LOGGER = logging.getLogger(__name__)
ACTIVE_IDLE_THRESHOLD_SECONDS = 5.0
PCAP_EXTENSIONS = {".pcap", ".pcapng"}
UNAVAILABLE_FEATURE_DEFAULTS = {
    "Fwd Avg Bytes/Bulk": 0.0,
    "Fwd Avg Packets/Bulk": 0.0,
    "Fwd Avg Bulk Rate": 0.0,
    "Bwd Avg Bytes/Bulk": 0.0,
    "Bwd Avg Packets/Bulk": 0.0,
    "Bwd Avg Bulk Rate": 0.0,
}


def load_network_artifacts(model_path: Path, scaler_path: Path):
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    return model, scaler


def analyze_network_capture(file_storage, model, scaler):
    suffix = Path(file_storage.filename or "").suffix.lower()
    if suffix not in PCAP_EXTENSIONS:
        raise ValueError("Only .pcap and .pcapng files are supported.")

    feature_logs = []
    saved_path = _persist_upload(file_storage, suffix)

    try:
        flows = _extract_flows(saved_path)
        if not flows:
            raise ValueError("No supported IPv4/IPv6 TCP or UDP flows were found in the uploaded capture.")

        rows = []
        for flow in flows:
            rows.append(flow.to_feature_row(feature_logs))

        feature_frame = pd.DataFrame(rows)
        aligned_frame = _align_features(feature_frame, scaler, feature_logs)
        scaled_features = scaler.transform(aligned_frame)

        predictions = model.predict(scaled_features)
        probabilities = model.predict_proba(scaled_features) if hasattr(model, "predict_proba") else None

        flow_results = []
        for index, flow in enumerate(flows):
            intrusion_probability = (
                float(probabilities[index][1])
                if probabilities is not None and len(probabilities[index]) > 1
                else float(predictions[index] == 1)
            )
            flow_results.append({
                "flow_id": flow.flow_id,
                "source": flow.forward_src,
                "destination": flow.forward_dst,
                "source_port": flow.forward_src_port,
                "destination_port": flow.forward_dst_port,
                "protocol": flow.protocol_name,
                "prediction": "intrusion" if int(predictions[index]) == 1 else "safe",
                "confidence": round(intrusion_probability if int(predictions[index]) == 1 else 1 - intrusion_probability, 4),
                "packet_count": flow.total_packets,
                "duration_seconds": round(flow.duration_seconds, 6),
            })

        overall_intrusion = any(item["prediction"] == "intrusion" for item in flow_results)
        relevant_flows = [
            item for item in flow_results
            if item["prediction"] == ("intrusion" if overall_intrusion else "safe")
        ]
        top_flow = max(relevant_flows, key=lambda item: item["confidence"])
        summary = {
            "prediction": "intrusion" if overall_intrusion else "safe",
            "confidence": top_flow["confidence"],
            "message": (
                "Potential malicious network activity detected in the uploaded capture."
                if overall_intrusion
                else "No malicious pattern was detected in the analyzed capture."
            ),
        }

        feature_logs = list(dict.fromkeys(feature_logs))

        return {
            "summary": summary,
            "flow_results": flow_results,
            "feature_logs": feature_logs,
            "feature_columns": list(aligned_frame.columns),
            "flows_analyzed": len(flow_results),
            "filename": secure_filename(file_storage.filename or "capture"),
        }
    finally:
        try:
            os.remove(saved_path)
        except OSError:
            LOGGER.warning("Could not remove temporary capture file: %s", saved_path)


def _persist_upload(file_storage, suffix: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        file_storage.save(temp_file.name)
        return temp_file.name


def _align_features(feature_frame: pd.DataFrame, scaler, feature_logs):
    feature_names = list(getattr(scaler, "feature_names_in_", []))
    if not feature_names:
        raise ValueError("Scaler metadata does not expose feature_names_in_.")

    feature_logs.append(
        "Training dataframe dtypes were not stored with the model artifacts; numeric features are aligned as float64 before scaling."
    )

    for feature_name, default_value in UNAVAILABLE_FEATURE_DEFAULTS.items():
        if feature_name not in feature_frame.columns:
            feature_frame[feature_name] = default_value
            feature_logs.append(f"{feature_name}: unavailable from raw PCAP flow state, defaulted to {default_value}.")

    missing_features = [name for name in feature_names if name not in feature_frame.columns]
    for feature_name in missing_features:
        feature_frame[feature_name] = 0.0
        feature_logs.append(f"{feature_name}: missing after feature engineering, defaulted to 0.0.")

    extra_features = [name for name in feature_frame.columns if name not in feature_names]
    if extra_features:
        feature_logs.append(f"Extra engineered features ignored because they are not part of the training schema: {', '.join(extra_features)}.")

    aligned = feature_frame.reindex(columns=feature_names, fill_value=0.0).copy()
    for column in aligned.columns:
        aligned[column] = pd.to_numeric(aligned[column], errors="coerce").fillna(0.0).astype(np.float64)
    return aligned


def _extract_flows(capture_path: str):
    flows = {}

    with PcapReader(capture_path) as reader:
        for packet in reader:
            packet_data = _packet_to_observation(packet)
            if packet_data is None:
                continue

            canonical_key, reverse_key, direction = _flow_keys(packet_data)
            if canonical_key in flows:
                flow = flows[canonical_key]
            elif reverse_key in flows:
                flow = flows[reverse_key]
                direction = "bwd"
            else:
                flow = FlowStats(packet_data)
                flows[canonical_key] = flow
                direction = "fwd"

            flow.add_packet(packet_data, direction)

    return list(flows.values())


def _packet_to_observation(packet):
    if IP in packet:
        ip_layer = packet[IP]
        src = ip_layer.src
        dst = ip_layer.dst
        ip_header_length = int(getattr(ip_layer, "ihl", 5)) * 4
        total_length = int(getattr(ip_layer, "len", len(bytes(packet))))
    elif IPv6 in packet:
        ip_layer = packet[IPv6]
        src = ip_layer.src
        dst = ip_layer.dst
        ip_header_length = 40
        total_length = len(bytes(packet))
    else:
        return None

    if TCP in packet:
        transport = packet[TCP]
        protocol = "TCP"
        src_port = int(transport.sport)
        dst_port = int(transport.dport)
        transport_header_length = int(getattr(transport, "dataofs", 5)) * 4
        payload_length = max(total_length - ip_header_length - transport_header_length, 0)
        flags = int(transport.flags)
        window = int(getattr(transport, "window", 0))
    elif UDP in packet:
        transport = packet[UDP]
        protocol = "UDP"
        src_port = int(transport.sport)
        dst_port = int(transport.dport)
        transport_header_length = 8
        payload_length = max(total_length - ip_header_length - transport_header_length, 0)
        flags = 0
        window = 0
    else:
        return None

    return {
        "timestamp": float(packet.time),
        "src": src,
        "dst": dst,
        "src_port": src_port,
        "dst_port": dst_port,
        "protocol": protocol,
        "length": float(total_length),
        "header_length": float(ip_header_length + transport_header_length),
        "transport_header_length": float(transport_header_length),
        "payload_length": float(payload_length),
        "flags": flags,
        "window": float(window),
    }


def _flow_keys(packet_data):
    forward = (
        packet_data["src"],
        packet_data["src_port"],
        packet_data["dst"],
        packet_data["dst_port"],
        packet_data["protocol"],
    )
    reverse = (
        packet_data["dst"],
        packet_data["dst_port"],
        packet_data["src"],
        packet_data["src_port"],
        packet_data["protocol"],
    )
    return forward, reverse, "fwd"


def _differences(values):
    if len(values) < 2:
        return []
    return [float(current - previous) for previous, current in zip(values[:-1], values[1:])]


def _stat_mean(values):
    return float(np.mean(values)) if values else 0.0


def _stat_std(values):
    return float(np.std(values)) if values else 0.0


def _stat_var(values):
    return float(np.var(values)) if values else 0.0


def _stat_min(values):
    return float(np.min(values)) if values else 0.0


def _stat_max(values):
    return float(np.max(values)) if values else 0.0


def _safe_divide(numerator, denominator):
    return float(numerator / denominator) if denominator else 0.0


def _flag_count(flags, mask):
    return 1 if flags & mask else 0


@dataclass
class FlowStats:
    first_packet: dict
    start_time: float = field(init=False)
    end_time: float = field(init=False)
    forward_src: str = field(init=False)
    forward_dst: str = field(init=False)
    forward_src_port: int = field(init=False)
    forward_dst_port: int = field(init=False)
    protocol_name: str = field(init=False)
    packet_timestamps: list = field(default_factory=list)
    packet_lengths: list = field(default_factory=list)
    fwd_timestamps: list = field(default_factory=list)
    bwd_timestamps: list = field(default_factory=list)
    fwd_lengths: list = field(default_factory=list)
    bwd_lengths: list = field(default_factory=list)
    fwd_header_lengths: list = field(default_factory=list)
    bwd_header_lengths: list = field(default_factory=list)
    fwd_transport_header_lengths: list = field(default_factory=list)
    all_flags: list = field(default_factory=list)
    fwd_flags: list = field(default_factory=list)
    bwd_flags: list = field(default_factory=list)
    active_durations: list = field(default_factory=list)
    idle_durations: list = field(default_factory=list)
    previous_timestamp: float = field(default=None)
    active_start_time: float = field(default=None)
    init_win_bytes_forward: float = field(default=0.0)
    init_win_bytes_backward: float = field(default=0.0)
    seen_forward_window: bool = field(default=False)
    seen_backward_window: bool = field(default=False)
    act_data_pkt_fwd: int = field(default=0)

    def __post_init__(self):
        self.start_time = self.first_packet["timestamp"]
        self.end_time = self.first_packet["timestamp"]
        self.forward_src = self.first_packet["src"]
        self.forward_dst = self.first_packet["dst"]
        self.forward_src_port = self.first_packet["src_port"]
        self.forward_dst_port = self.first_packet["dst_port"]
        self.protocol_name = self.first_packet["protocol"]

    @property
    def flow_id(self):
        return f"{self.forward_src}:{self.forward_src_port} -> {self.forward_dst}:{self.forward_dst_port} ({self.protocol_name})"

    @property
    def duration_seconds(self):
        return max(float(self.end_time - self.start_time), 0.0)

    @property
    def total_packets(self):
        return len(self.packet_lengths)

    def add_packet(self, packet_data, direction):
        timestamp = packet_data["timestamp"]
        self.packet_timestamps.append(timestamp)
        self.packet_lengths.append(packet_data["length"])
        self.all_flags.append(packet_data["flags"])
        self.end_time = timestamp

        if self.active_start_time is None:
            self.active_start_time = timestamp
        if self.previous_timestamp is not None:
            gap = float(timestamp - self.previous_timestamp)
            if gap > ACTIVE_IDLE_THRESHOLD_SECONDS:
                self.active_durations.append(max(self.previous_timestamp - self.active_start_time, 0.0))
                self.idle_durations.append(gap)
                self.active_start_time = timestamp
        self.previous_timestamp = timestamp

        if direction == "fwd":
            self.fwd_timestamps.append(timestamp)
            self.fwd_lengths.append(packet_data["length"])
            self.fwd_header_lengths.append(packet_data["header_length"])
            self.fwd_transport_header_lengths.append(packet_data["transport_header_length"])
            self.fwd_flags.append(packet_data["flags"])
            if packet_data["payload_length"] > 0:
                self.act_data_pkt_fwd += 1
            if not self.seen_forward_window:
                self.init_win_bytes_forward = packet_data["window"]
                self.seen_forward_window = True
        else:
            self.bwd_timestamps.append(timestamp)
            self.bwd_lengths.append(packet_data["length"])
            self.bwd_header_lengths.append(packet_data["header_length"])
            self.bwd_flags.append(packet_data["flags"])
            if not self.seen_backward_window:
                self.init_win_bytes_backward = packet_data["window"]
                self.seen_backward_window = True

    def to_feature_row(self, feature_logs):
        if self.previous_timestamp is not None and self.active_start_time is not None:
            self.active_durations.append(max(self.previous_timestamp - self.active_start_time, 0.0))

        flow_iat = _differences(self.packet_timestamps)
        fwd_iat = _differences(self.fwd_timestamps)
        bwd_iat = _differences(self.bwd_timestamps)
        duration = self.duration_seconds

        if not self.bwd_lengths:
            feature_logs.append(f"{self.flow_id}: backward-direction features are absent because this flow has no reverse packets.")

        row = {
            "Destination Port": float(self.forward_dst_port),
            "Flow Duration": duration,
            "Total Fwd Packets": float(len(self.fwd_lengths)),
            "Total Backward Packets": float(len(self.bwd_lengths)),
            "Total Length of Fwd Packets": float(sum(self.fwd_lengths)),
            "Total Length of Bwd Packets": float(sum(self.bwd_lengths)),
            "Fwd Packet Length Max": _stat_max(self.fwd_lengths),
            "Fwd Packet Length Min": _stat_min(self.fwd_lengths),
            "Fwd Packet Length Mean": _stat_mean(self.fwd_lengths),
            "Fwd Packet Length Std": _stat_std(self.fwd_lengths),
            "Bwd Packet Length Max": _stat_max(self.bwd_lengths),
            "Bwd Packet Length Min": _stat_min(self.bwd_lengths),
            "Bwd Packet Length Mean": _stat_mean(self.bwd_lengths),
            "Bwd Packet Length Std": _stat_std(self.bwd_lengths),
            "Flow Bytes/s": _safe_divide(sum(self.packet_lengths), duration),
            "Flow Packets/s": _safe_divide(len(self.packet_lengths), duration),
            "Flow IAT Mean": _stat_mean(flow_iat),
            "Flow IAT Std": _stat_std(flow_iat),
            "Flow IAT Max": _stat_max(flow_iat),
            "Flow IAT Min": _stat_min(flow_iat),
            "Fwd IAT Total": float(sum(fwd_iat)),
            "Fwd IAT Mean": _stat_mean(fwd_iat),
            "Fwd IAT Std": _stat_std(fwd_iat),
            "Fwd IAT Max": _stat_max(fwd_iat),
            "Fwd IAT Min": _stat_min(fwd_iat),
            "Bwd IAT Total": float(sum(bwd_iat)),
            "Bwd IAT Mean": _stat_mean(bwd_iat),
            "Bwd IAT Std": _stat_std(bwd_iat),
            "Bwd IAT Max": _stat_max(bwd_iat),
            "Bwd IAT Min": _stat_min(bwd_iat),
            "Fwd PSH Flags": float(sum(_flag_count(flags, 0x08) for flags in self.fwd_flags)),
            "Bwd PSH Flags": float(sum(_flag_count(flags, 0x08) for flags in self.bwd_flags)),
            "Fwd URG Flags": float(sum(_flag_count(flags, 0x20) for flags in self.fwd_flags)),
            "Bwd URG Flags": float(sum(_flag_count(flags, 0x20) for flags in self.bwd_flags)),
            "Fwd Header Length": float(sum(self.fwd_header_lengths)),
            "Bwd Header Length": float(sum(self.bwd_header_lengths)),
            "Fwd Packets/s": _safe_divide(len(self.fwd_lengths), duration),
            "Bwd Packets/s": _safe_divide(len(self.bwd_lengths), duration),
            "Min Packet Length": _stat_min(self.packet_lengths),
            "Max Packet Length": _stat_max(self.packet_lengths),
            "Packet Length Mean": _stat_mean(self.packet_lengths),
            "Packet Length Std": _stat_std(self.packet_lengths),
            "Packet Length Variance": _stat_var(self.packet_lengths),
            "FIN Flag Count": float(sum(_flag_count(flags, 0x01) for flags in self.all_flags)),
            "SYN Flag Count": float(sum(_flag_count(flags, 0x02) for flags in self.all_flags)),
            "RST Flag Count": float(sum(_flag_count(flags, 0x04) for flags in self.all_flags)),
            "PSH Flag Count": float(sum(_flag_count(flags, 0x08) for flags in self.all_flags)),
            "ACK Flag Count": float(sum(_flag_count(flags, 0x10) for flags in self.all_flags)),
            "URG Flag Count": float(sum(_flag_count(flags, 0x20) for flags in self.all_flags)),
            "CWE Flag Count": float(sum(_flag_count(flags, 0x80) for flags in self.all_flags)),
            "ECE Flag Count": float(sum(_flag_count(flags, 0x40) for flags in self.all_flags)),
            "Down/Up Ratio": _safe_divide(len(self.bwd_lengths), len(self.fwd_lengths)),
            "Average Packet Size": _stat_mean(self.packet_lengths),
            "Avg Fwd Segment Size": _stat_mean(self.fwd_lengths),
            "Avg Bwd Segment Size": _stat_mean(self.bwd_lengths),
            "Fwd Header Length.1": float(sum(self.fwd_header_lengths)),
            "Subflow Fwd Packets": float(len(self.fwd_lengths)),
            "Subflow Fwd Bytes": float(sum(self.fwd_lengths)),
            "Subflow Bwd Packets": float(len(self.bwd_lengths)),
            "Subflow Bwd Bytes": float(sum(self.bwd_lengths)),
            "Init_Win_bytes_forward": float(self.init_win_bytes_forward),
            "Init_Win_bytes_backward": float(self.init_win_bytes_backward),
            "act_data_pkt_fwd": float(self.act_data_pkt_fwd),
            "min_seg_size_forward": _stat_min(self.fwd_transport_header_lengths),
            "Active Mean": _stat_mean(self.active_durations),
            "Active Std": _stat_std(self.active_durations),
            "Active Max": _stat_max(self.active_durations),
            "Active Min": _stat_min(self.active_durations),
            "Idle Mean": _stat_mean(self.idle_durations),
            "Idle Std": _stat_std(self.idle_durations),
            "Idle Max": _stat_max(self.idle_durations),
            "Idle Min": _stat_min(self.idle_durations),
        }

        row.update(UNAVAILABLE_FEATURE_DEFAULTS)
        return row
