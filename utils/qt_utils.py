def get_top_most_parent(widget):
    top_widget = widget
    while top_widget.parentWidget():
        top_widget = top_widget.parentWidget()
    print(top_widget)
    return top_widget