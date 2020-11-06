import json

def save(widget, json_file):
	d = {}
	d['ipe_size'] = widget.ipe_size.currentText()
	d['extend_length'] = widget.extend_length.value()
	d['extend_plate_len_above'] = widget.extend_plate_len_above.value()
	d['extend_plate_len_below'] = widget.extend_plate_len_below.value()
	d['connection_ipe_length'] = widget.connection_ipe_length.value()
	d['connection_ipe_above'] = widget.connection_ipe_above.value()
	d['deltax'] = widget.deltax.value()
	d['pa_baz'] = widget.pa_baz.isChecked()


	with open(json_file, 'w') as f:
		json.dump(d, f)

def load(widget, json_file):
	with open(json_file, 'r') as f:
		d = json.load(f)

	index = widget.ipe_size.findText(d['ipe_size'])
	widget.ipe_size.setCurrentIndex(index)
	widget.extend_length.setValue(d['extend_length'])
	widget.extend_plate_len_above.setValue(d.get('extend_plate_len_above', .8))
	widget.extend_plate_len_below.setValue(d.get('extend_plate_len_below', .8))
	widget.connection_ipe_length.setValue(d['connection_ipe_length'])
	widget.connection_ipe_above.setValue(d['connection_ipe_above'])
	widget.deltax.setValue(d['deltax'])
	widget.pa_baz.setChecked(d['pa_baz'])

