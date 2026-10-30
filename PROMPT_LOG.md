# Prompt Log

## AI Tools Used

- **Claude Opus:** Used for generating the initial implementation plan and deciding the project structure and development approach.
- **Claude Sonnet 5.5:** Used for implementing the application module by module, with code review and testing along the way.

Section 1 (data sanitization) was implemented independently without AI assistance, as required by the assessment.

## Section 3 – AI Prompting & Charting

### Initial Prompt

"Write a Python script that reads the generated summary.json file and creates a bar chart comparing the average temperature of each device using matplotlib. Save the chart as a PNG file."

### Issue in the Initial Output

The initial chart was quite basic. The X-axis labels needed better formatting, and the chart could be made more readable with proper spacing and value labels.

### Follow-up Prompt

"The device labels are overlapping and the chart is missing some formatting. Rotate the X-axis labels by 45 degrees, add a proper title and axis labels, display the temperature values above each bar, and adjust the layout so everything remains readable."

> The x-axis labels overlap and get cut off when device IDs are long, and the chart has no title
> or x-axis label. Rotate the labels 45 degrees and right-align them, call `tight_layout`, add a
> title and axis labels, show each bar's value, and make the figure width scale with the number
> of devices.

### 4. Review after the fix

- Re-rendered both the stress dataset and the real sample output: labels are readable and nothing
  is clipped.
- Spotted a smaller inconsistency myself: bar labels showed one decimal (56.4) while the terminal
  table and JSON show two (56.38). Changed the label format to two decimals so all three agree.
- Added tests that assert the figure has a title, axis labels, rotated tick labels and one bar per
  device, so the layout fixes don't regress.
- Kept matplotlib an optional dependency (lazy import, headless `Agg` backend) so the core tool
  still runs with no third-party packages.

### Final Review

After reviewing the generated chart, I checked the layout, labels, and displayed values to ensure they were readable and consistent with the JSON output.

The final chart was saved as `output/avg_temperature.png`.