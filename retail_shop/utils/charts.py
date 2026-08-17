from frappe.utils import flt


def bar_chart(rows, label_field, dataset_specs, limit=20):
	"""dataset_specs: list of (fieldname, dataset_label) tuples.
	Assumes rows are already sorted in the order they should appear."""
	rows = rows[:limit]
	return {
		"data": {
			"labels": [row.get(label_field) for row in rows],
			"datasets": [
				{"name": label, "values": [flt(row.get(fieldname)) for row in rows]}
				for fieldname, label in dataset_specs
			],
		},
		"type": "bar",
	}


def date_series_line_chart(rows, date_field, value_field, dataset_label):
	"""Sums value_field per distinct date_field value, plotted oldest to newest."""
	totals = {}
	for row in rows:
		date = row.get(date_field)
		if not date:
			continue
		totals[date] = totals.get(date, 0) + flt(row.get(value_field))

	dates = sorted(totals.keys())
	return {
		"data": {
			"labels": [str(date) for date in dates],
			"datasets": [{"name": dataset_label, "values": [flt(totals[date]) for date in dates]}],
		},
		"type": "line",
	}
