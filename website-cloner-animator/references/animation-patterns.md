# Animation Pattern Reference

Concrete techniques and Framer Motion / Tailwind patterns to draw from when building the animation layer. Pick what fits the design — don't apply every pattern to every page; over-animating reads as cheap, not premium.

## Hero Animations

**Staggered fade-up entrance** (headline, subhead, CTA appear in sequence on load):
```tsx
const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.12, delayChildren: 0.1 } },
};
const item = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] } },
};
// <motion.div variants={container} initial="hidden" animate="show">
//   <motion.h1 variants={item}>...</motion.h1>
//   <motion.p variants={item}>...</motion.p>
// </motion.div>
```

**Blur reveal** — pair opacity with a small blur-to-sharp transition for a softer entrance:
```tsx
initial={{ opacity: 0, filter: "blur(8px)" }}
animate={{ opacity: 1, filter: "blur(0px)" }}
transition={{ duration: 0.6, ease: "easeOut" }}
```

**Background motion** — floating gradient blobs (pure CSS, GPU-cheap):
```css
@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(20px, -30px) scale(1.05); }
}
.gradient-blob { animation: float 8s ease-in-out infinite; }
```
Keep blobs blurred (`blur-3xl`), low opacity, and behind content (`-z-10`) so they add depth without competing for attention.

## Scroll Animations

Always gate on viewport entry and fire once — use `whileInView` with `viewport={{ once: true, margin: "-80px" }}` (the negative margin triggers slightly before the element is fully visible, which feels more responsive).

**Fade up on scroll:**
```tsx
<motion.div
  initial={{ opacity: 0, y: 24 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, margin: "-80px" }}
  transition={{ duration: 0.5 }}
>
```

**Staggered card grid** — wrap the grid in a parent with `staggerChildren`, each card uses the `item` variant from above, parent triggers via `whileInView`.

**Mask/clip reveal** for images or section dividers:
```tsx
initial={{ clipPath: "inset(0 0 100% 0)" }}
whileInView={{ clipPath: "inset(0 0 0% 0)" }}
transition={{ duration: 0.7, ease: [0.65, 0, 0.35, 1] }}
```

## Card Interactions

```css
.card {
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px -8px rgb(0 0 0 / 0.18);
}
```
For a tilt effect, use Framer Motion's `useMotionValue` + `useTransform` on mouse position to drive small `rotateX`/`rotateY` (keep the rotation under ~6deg — anything more looks gimmicky on a content card).

## Button Interactions

```tsx
<motion.button
  whileHover={{ scale: 1.03 }}
  whileTap={{ scale: 0.97 }}
  transition={{ duration: 0.15 }}
  className="transition-shadow hover:shadow-[0_0_24px_rgba(99,102,241,0.4)]"
>
```
Active/tap feedback (`whileTap`) matters as much as hover — it's what makes a button feel physically responsive on touch devices where hover doesn't exist.

## Navigation

- Underline motion: animate a `layoutId`-shared underline element between nav links so it slides rather than jump-cuts between active states.
- Mobile menu: animate height/opacity of the panel (`AnimatePresence` + `initial`/`animate`/`exit`), and stagger the menu items in the same way as hero content.
- Page transitions (if using App Router): wrap route content in `AnimatePresence mode="wait"` with a brief fade/slide, but keep it under ~250ms — slow page transitions make an app feel laggy, not premium.

## Timing cheatsheet

| Interaction | Duration | Easing |
|---|---|---|
| Hover/tap feedback | 100-200ms | ease-out |
| Scroll reveal | 400-600ms | `[0.16, 1, 0.3, 1]` (expo-out) |
| Stagger gap between children | 80-150ms | — |
| Page/section transition | 200-300ms | ease-in-out |
| Ambient background motion | 6-12s loop | ease-in-out |

If a duration in your code is outside these ranges, there should be a deliberate reason for it.
