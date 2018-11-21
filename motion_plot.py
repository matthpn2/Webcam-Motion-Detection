from motion_capture import df
from bokeh.plotting import figure, output_file, show
from bokeh.models import HoverTool, ColumnDataSource

# convert the datetimes to readable time strings for hovertool
df["start_time"] = df["start"].dt.strftime("%Y-%m-%d %H:%M:%S")
df["end_time"] = df["end"].dt.strftime("%Y-%m-%d %H:%M:%S")

# set the data source as the data frame
cds = ColumnDataSource(df)

# create figure object and initialize its settings
plot = figure(x_axis_type = "datetime", height = 100, width = 500, sizing_mode = "scale_width", title = "Video Motion Graph")
plot.yaxis.minor_tick_line_color = None
plot.ygrid[0].ticker.desired_num_ticks = 1

# create hover tool box that highlights the start and end times of the plot
hover = HoverTool(tooltips = [("start", "@start_time"), ("end", "@end_time")])
plot.add_tools(hover)

# plot the glyphs
glyph = plot.quad(left = "start", right = "end", bottom = 0, top = 1, color = "green", source = cds)

# save and display the plot graph
output_file("motion_graph.html")
show(plot)