import griffe
from griffe2md import ConfigDict, render_object_docs

statsforecast = griffe.load("statsforecast")
coreforecast = griffe.load("coreforecast")

print(
    render_object_docs(
        statsforecast["models.AutoARIMA"],
        ConfigDict(
            heading_level=3,
            members=["fit", "predict", "predict_in_sample", "forecast", "forward"],
            show_root_heading=True,
            show_source=True,
            docstring_section_style= 'table',
            summary={
                'functions':False
            }
        ),
    )
)

# print(
#     render_object_docs(
#         coreforecast["coreforecast.scalers.boxcox_lambda"],
#         ConfigDict(
#             heading_level=3,
#             show_root_heading=True,
#             show_source=True,
#             docstring_section_style= 'table',
#             summary={
#                 'functions':False
#             }
#         ),
#     )
# )