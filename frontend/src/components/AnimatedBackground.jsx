import React, { useEffect, useRef } from 'react'

export default function AnimatedBackground() {
  const containerRef = useRef(null)

  useEffect(() => {
    // Wait for Vanta to be available
    const initVanta = () => {
      if (containerRef.current && window.VANTA && window.THREE) {
        window.VANTA.NET({
          el: containerRef.current,
          mouseControls: false,
          touchControls: false,
          gyroControls: false,
          minHeight: 200.0,
          minWidth: 200.0,
          scale: 2.0,
          scaleMobile: 1.5,
          color: 0x3d1675,
          backgroundColor: 0x100d28,
          points: 4.0,
          maxDistance: 12.0,
          spacing: 22.0,
          forceAnimate: true,
        })
      } else if (!window.VANTA || !window.THREE) {
        // Retry if scripts not loaded yet
        setTimeout(initVanta, 500)
      }
    }

    initVanta()
  }, [])

  return (
    <div
      ref={containerRef}
      className="animated-bg"
      aria-hidden="true"
      style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100vh' }}
    />
  )
}
