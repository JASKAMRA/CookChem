# Responsive Visual QA

## Browser checks

| Layout | Measured CSS viewport | Document width | Result |
|---|---:|---:|---|
| Desktop | 2304 × 1042 | 2304 px | No horizontal overflow; all eight module pages rendered during QA |
| Tablet | 810 × 1200 | 810 px | Overview hero and theme cards fit; no horizontal overflow |
| Mobile | 390 × 840 | 390 px | Overview cards stack; Scientific Limitations image fits; Existing ML metric cards, chart, table and evidence badges fit; no horizontal overflow |

The tablet viewport was produced by a browser scale factor of 1.5 from the configured viewport; reported values are the CSS viewport measured in the page. The mobile Existing ML Results main column was 390 px wide; metric cards were 310 px wide and the furthest evidence/dataset badge ended within 335 px of the column origin.

## Images and icons

- Six project-local WebP illustrations were loaded in their intended modules. Browser checks reported complete image loads and nonzero natural dimensions.
- All eight sidebar destinations retained their original labels and had eight distinct computed outline icon masks.
- Landing CTA icons, filter icons, module-header icons, cooking method theme icons, model identity icons and status badges were present in the rendered DOM.
- Responsive image styling preserves intrinsic proportions and constrains images to their Streamlit content columns.

## Browser errors and screenshot availability

No Streamlit exception or traceback was present in the rendered pages. The browser console query returned no warning or error entries. Browser screenshot capture timed out, so no screenshot file is included; confirmation used the live rendered DOM, computed styles, image load state and measured geometry. Viewports were emulated; no second physical device was available.
