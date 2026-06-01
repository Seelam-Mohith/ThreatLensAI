import React from 'react'

export default function AnimatedBackground() {
  return (
    <div className="animated-bg" aria-hidden="true">
      <div className="animated-bg__blob animated-bg__blob--one" />
      <div className="animated-bg__blob animated-bg__blob--two" />
      <div className="animated-bg__blob animated-bg__blob--three" />
    </div>
  )
}
