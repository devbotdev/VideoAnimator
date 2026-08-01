# Engine Capabilities

This document outlines the technical capabilities and limitations of the Animation Engine. Creative agents (Concept Director, Visual Metaphor Designer, Storyboard Artist, Animation Planner) must adhere to these constraints when designing scenes.

## 1. Available Objects
- **Basic Primitives:**
  - `Circle` (radius)
  - `Rectangle` (width, height, corner_radius)
  - `Line` (end_x, end_y)
  - `Polyline` (points)
  - `Path` (d - SVG path data)
  - `Text` (content, font_size, font_family, text_anchor, text_alignment)
  - `Arrow` (start_x, start_y, end_x, end_y, arrowhead_size)
- **Composite Objects:**
  - `Group` (children)
  - `StickFigure` (head, body, arms, legs; specialized animation methods)

**Common Properties (All Objects):**
- Position: `x`, `y`
- Transform: `rotation`, `scale`
- Visibility: `opacity` (0.0 to 1.0), `visibility` (bool)
- Styling: `style` (fill_color, stroke_color, stroke_width, line_cap, line_join)

## 2. Available Animations & Actions
- **General Actions (All Objects):**
  - `move` (absolute or relative)
  - `fade_in` / `fade_out`
  - `scale` / `grow`
  - `rotate`
- **Object-Specific Actions:**
  - `draw` (Path objects only)
  - `highlight` / `shake` (BaseObject)
  - `walk` / `point` / `wave` / `think` / `celebrate` / `idle` / `enter` / `exit` (StickFigure only)
- **Camera Actions:**
  - `camera_pan`
  - `camera_zoom`
  - `camera_focus`

## 3. Rendering Style
- Vector-based SVG animation exported as MP4.
- Scene-based structure.

## 4. Known Limitations & Constraints
- **Conceptual Metaphors:** No support for photorealistic or complex 3D assets. Use circles, lines, and paths to represent complex ideas (e.g., a planet is a circle, movement is lines).
- **Streaming Renderer:** The rendering engine cannot seek backward. Animations must be planned linearly.
- **Interactivity:** No support for interactive elements. Only static MP4 video output.
- **Complexity:** Highly complex scenes with thousands of objects may impact rendering time. Prefer simpler, clearer visual metaphors.
