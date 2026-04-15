# Design System: Neon Mysticism & Cosmic Satire

## 1. Overview & Creative North Star
**Creative North Star: "The Psychedelic Oracle"**

This design system is a rejection of the "clean and corporate" web. It is a high-end, editorial fusion of mystical tarot tradition and irreverent gaming UI. We are moving away from flat, static layouts toward a **living, breathing digital ritual.** 

The experience must feel like a premium, "haunted" arcade machine. We break the template look through **intentional depth**, **chromatic vibrance**, and **dynamic state changes**. This isn't just a utility; it's an immersive performance where the UI reacts to the "fate" of the user.

---

## 2. Colors & Atmospheric Depth
Our palette is rooted in the void (`#0f0d16`) but punctuated by "Mood Accents" that shift based on the card’s energy.

### The Role of Accents
*   **Primary (`#df8eff`):** Used for "The Fool’s Journey"—standard navigation and mystical insights.
*   **Secondary (`#00eefc`):** Used for "Positive Fate"—logic, clarity, and uplifting readings.
*   **Tertiary (`#deffab`):** Used for "The Absurd"—humorous results and chaotic energy.

### The Rules of Surface & Light
*   **The "No-Line" Rule:** 1px solid borders are strictly forbidden for sectioning. Separation must be achieved through background shifts (e.g., a `surface-container-low` card nested within a `surface` background).
*   **The Glass & Gradient Rule:** High-end surfaces must use **Glassmorphism**. Apply `surface-container-high` at 60% opacity with a `20px` backdrop-blur. 
*   **Signature Textures:** Backgrounds should never be flat. Use a subtle radial gradient of `primary-container` at 10% opacity in the corners to create a "glowing" soul within the dark void.

---

## 3. Typography: The Bold Prophecy
We use a high-contrast typographic scale to balance authority with modern "game-ui" aesthetics.

*   **Display (Space Grotesk):** Our "Voice of Fate." Use `display-lg` for card titles and major headers. It is bold, geometric, and unapologetic.
*   **Headline (Space Grotesk):** Used for section starts. These should often be paired with a `secondary` or `tertiary` text shadow to create a subtle neon hum.
*   **Body (Manrope):** Our "Subtle Sarcasm." Manrope provides the readability needed for long, humorous tarot descriptions. It feels modern and human.
*   **Labels (Plus Jakarta Sans):** Used for technical metadata (e.g., "Card VIII"). These should always be uppercase with a `0.05em` letter spacing to feel like a premium game HUD.

---

## 4. Elevation & Depth: Tonal Layering
In this system, depth is not a shadow—it is an **emission of light.**

*   **The Layering Principle:** Stack `surface-container` tokens to create hierarchy. A `surface-container-lowest` card (the "void") sitting on a `surface-container-high` section creates a recessed, "embedded" look.
*   **Ambient Shadows:** Use large, diffused glows instead of shadows. A floating card should have a `24px` blur shadow using the `primary` token at 12% opacity.
*   **The "Ghost Border" Fallback:** If a boundary is needed for accessibility, use the `outline-variant` token at **15% opacity**. This creates a "whisper" of a container rather than a hard cage.
*   **3D CSS Interactions:** Cards should utilize a slight `perspective(1000px) rotateX()` on hover to mimic physical tarot handling.

---

## 5. Components

### The Kinetic Card (Component: Card)
*   **Style:** No dividers. Use `surface-container-highest` for the header area and `surface-container-low` for the body.
*   **Edge:** Use a "Glowing Border" on hover—a 1px inner box-shadow using the `secondary` or `tertiary` token.

### Ethereal Buttons (Component: Button)
*   **Primary:** A gradient from `primary` to `primary-container`. High roundedness (`full`). No border.
*   **Secondary:** Glassmorphic. `surface-container-high` with a 20% opacity `outline`.
*   **Interaction:** On press, the button should "pulse," increasing the backdrop-blur value.

### Fate Chips (Component: Chips)
*   **Visual:** Small, pill-shaped containers using `surface-variant`.
*   **Typography:** `label-md` in `on-surface-variant`. 
*   **Rule:** When selected, they should glow with the color of the current "mood" accent.

### Input Fields (Component: Text Input)
*   **Visual:** A "sunken" look. Use `surface-container-lowest` background.
*   **State:** The label (`label-md`) should glow in `secondary` (Cyan) when the field is focused, signaling "Active Consciousness."

### Ritual Tooltips (Component: Tooltip)
*   **Style:** Sharp corners (`sm` scale) to contrast with rounded buttons. 
*   **Color:** `inverse-surface` with `inverse-on-surface` text. Apply a `primary` neon underline of 2px.

---

## 6. Do’s and Don’ts

### Do:
*   **Do** use asymmetrical layouts. Let a card overlap a headline to create a sense of organic "spread."
*   **Do** use particle textures (CSS-based dust or stars) in the background of `surface-container-lowest` areas.
*   **Do** lean into the humor. Use `tertiary` (Lime) for "Silly" or "Ridiculous" fates to visually separate them from "Serious" ones.

### Don’t:
*   **Don't** use 100% black (`#000000`) except for the deepest "sunken" containers. Use the `surface` token (`#0f0d16`) to maintain depth.
*   **Don't** use standard "drop shadows." If it doesn't look like a neon glow or a soft ambient occlusion, it doesn't belong.
*   **Don't** use dividers or horizontal rules. If you need to separate content, use a 48px vertical gap or a subtle shift from `surface-container-low` to `surface-container-high`.

---

## 7. Signature Interaction: The Mood Shift
The most critical rule: The `primary`, `secondary`, and `tertiary` tokens are **interchangeable variables.** If a user draws a "Chaos" card, the `secondary` neon (Cyan) across the *entire* app should transition to `tertiary` (Lime Green). This "Tonal Takeover" ensures the UI is as unpredictable as fate itself.