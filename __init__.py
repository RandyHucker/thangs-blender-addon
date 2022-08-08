# <pep8 compliant>
import webbrowser
from bpy.types import (Panel,
                       PropertyGroup,
                       Operator,
                       )
from bpy.props import (StringProperty,
                       PointerProperty,
                       FloatVectorProperty,
                       )
from mathutils import Vector
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from bpy.app.handlers import persistent
import math
import bpy
from urllib.request import urlopen
import urllib.request
import urllib.parse
import requests
import os
import importlib
import threading
import bpy.utils.previews
import asyncio
from .thangs_fetcher import ThangsFetcher
import time


bl_info = {
    "name": "Thangs Model Search",
    "author": "Thangs",
    "version": (0, 1, 0),
    "blender": (3, 2, 0),
    "location": "VIEW 3D > Sidebar > Thangs Search",
    "description": "Import Thangs Models (.glb, .usdz, .stl)",
    "warning": "",
    "doc_url": "N/A",
    "category": "Import/Export",
}


def confirm_list(object):
    """ if single item passed, convert to list """
    if type(object) not in (list, tuple):
        object = [object]
    return object


def tag_redraw_areas(area_types: iter = ["ALL"]):
    """ run tag_redraw for given area types """
    if fetcher.searching == False:
        if fetcher.thangs_ui_mode == 'SEARCH':
            fetcher.thangs_ui_mode = 'VIEW'
    area_types = confirm_list(area_types)
    screens = [bpy.context.screen] if bpy.context.screen else bpy.data.screens
    print(screens)
    for screen in screens:
        for area in screen.areas:
            for area_type in area_types:
                if area_type == "ALL" or area.type == area_type:
                    area.tag_redraw()


def on_complete_search():
    tag_redraw_areas()
    return


fetcher = ThangsFetcher(callback=on_complete_search)
#URLlist = []
ButtonSearch = "Search"
# Added
PageNumber = fetcher.PageNumber
#Results = fetcher.Results

pcoll = fetcher.pcoll

PageTotal = fetcher.PageTotal
fetcher.thangs_ui_mode = 'SEARCH'


def setSearch():
    global ButtonSearch
    ButtonSearch = bpy.context.scene.thangs_model_search
    return None


def LastPage():
    if fetcher.searching:
        return None

    if fetcher.PageNumber == fetcher.PageTotal:
        return None
    else:
        fetcher.PageNumber = fetcher.PageTotal
        fetcher.search(fetcher.query)
        return None


def IncPage():
    if fetcher.searching:
        return None
    # Pages = Results/7
    if fetcher.PageNumber < fetcher.PageTotal:
        fetcher.PageNumber = fetcher.PageNumber + 1
        fetcher.search(fetcher.query)
    return None


def DecPage():
    if fetcher.searching:
        return None
    if fetcher.PageNumber == 1:
        return None
    fetcher.PageNumber = fetcher.PageNumber - 1
    fetcher.search(fetcher.query)
    return None


def FirstPage():
    if fetcher.searching:
        return None
    fetcher.PageNumber = 1
    fetcher.search(fetcher.query)


class SearchButton(bpy.types.Operator):
    """Searches Thangs for Meshes"""
    bl_idname = "search.thangs"
    bl_label = " "

    def execute(self, context):
        setSearch()
        return {'FINISHED'}


class LastPageChange(bpy.types.Operator):
    """Go to Last Page"""
    bl_idname = "lastpage.thangs"
    bl_label = "Last Page"

    def execute(self, context):
        LastPage()
        return {'FINISHED'}


class IncPageChange(bpy.types.Operator):
    """Go to Next Page"""
    bl_idname = "incpage.thangs"
    bl_label = "Next Page"

    def execute(self, context):
        IncPage()
        return {'FINISHED'}


class DecPageChange(bpy.types.Operator):
    """Go to Previous Page"""
    bl_idname = "decpage.thangs"
    bl_label = "Previous Page"

    def execute(self, context):
        DecPage()
        return {'FINISHED'}


class FirstPageChange(bpy.types.Operator):
    """Go to First Page"""
    bl_idname = "firstpage.thangs"
    bl_label = "First Page"

    def execute(self, context):
        FirstPage()
        return {'FINISHED'}


class ThangsLink(bpy.types.Operator):
    """Click to continue on Thangs"""
    bl_idname = "link.thangs"
    #bl_label = "Search"
    bl_label = "Redirect to Thangs"

    def execute(self, context):
        webbrowser.open("https://thangs.com/search/"+fetcher.query +
                        "/?utm_source=blender&utm_medium=referral&utm_campaign=blender_extender&scope=all", new=0, autoraise=True)
        return {'FINISHED'}


def enum_previews_from_thangs_api(self, context):
    """Thangs API callback"""
    global fetcher

    if context is None:
        return fetcher.enumItems

    wm = context.window_manager
    #directory = bpy.context.scene.my_string_prop

    return fetcher.pcoll.Mode


icon_collections = {}
icons_dict = bpy.utils.previews.new()
icon_collections["main"] = icons_dict
icons_dict = icon_collections["main"]
icons_dir = os.path.join(os.path.dirname(__file__), "icons")
icons_dict.load("ThangsT", os.path.join(icons_dir, "T.png"), 'IMAGE')


# class Thangs_OT_view(Operator):
#     """View Search Results"""

#     bl_idname = "thangs.view_mode"
#     bl_label = "View"
#     bl_description = " "
#     bl_options = {'REGISTER', 'INTERNAL'}

#     next_mode: StringProperty()

#     def execute(self, context):
#         print("Changed Mode to VIEW")
#         global thangs_ui_mode
#         self.next_mode == 'VIEW'
#         thangs_ui_mode = self.next_mode

#         context.area.tag_redraw()
#         return {'FINISHED'}

class THANGS_OT_search_invoke(Operator):
    """Search for Query"""

    bl_idname = "thangs.search_invoke"
    bl_label = "Clear Search   "
    bl_description = "Clear the Search"
    bl_options = {'REGISTER', 'INTERNAL'}

    next_mode: StringProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    # def invoke(self, context, event):
    #     global thangs_ui_mode
    #     # If adding a new plant, start off with the defaults
    #     if thangs_ui_mode == 'SEARCH':
    #         self.next_mode == 'VIEW'
    #     else:
    #         self.next_mode == 'SEARCH'
    #     thangs_ui_mode = self.next_mode
    #     context.area.tag_redraw()
    #     return {'RUNNING_MODAL'}

    def execute(self, context):
        if fetcher.searching:
            return {'FINISHED'}
        print("Changed Mode to " + str(fetcher.thangs_ui_mode))
        # If adding a new plant, start off with the defaults
        if fetcher.thangs_ui_mode == 'SEARCH':
            self.next_mode == 'VIEW'
        else:
            self.next_mode == 'SEARCH'
        fetcher.thangs_ui_mode = self.next_mode

        context.area.tag_redraw()
        return {'FINISHED'}


class THANGS_PT_model_display(bpy.types.Panel):
    bl_label = "Thangs Model Search"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Thangs Search"

    #fetcher.context = bpy.context.window

    def next_mode(self, op):
        # modes: ADD, EDIT, SELECT, SELECT_ADD, VIEW
        ops = ['SEARCH', 'VIEW']
        m = fetcher.thangs_ui_mode
        nm = m

        if op not in ops:
            return nm

        if m == 'SEARCH':
            nm = 'VIEW'
        elif m == 'VIEW':
            nm = 'SEARCH'
            if op == 'CANCEL':
                nm = 'VIEW'
        return nm

    def drawView(self, context):
        wm = context.window_manager

        layout = self.layout
        #layout.ui_units_x = 8.5

        if fetcher.searching == True:
            layout.active = False
            SearchingLayout = self.layout
            SearchingRow = SearchingLayout.row(align=True)
            SearchingRow.label(
                text="Searching...")

        if fetcher.totalModels != 0:
            if fetcher.searching == False:
                row = layout.row()
                row.label(text="Found " +
                          str(fetcher.totalModels)+"+ results for")
                row.scale_x = .2
                row.ui_units_x = .1
                row.separator(factor=4)
                row.operator(
                    "link.thangs", icon_value=icons_dict["ThangsT"].icon_id)

                row = layout.row()
                row.label(
                    text="“"+bpy.context.scene.thangs_model_search+"” on Thangs")

                row = layout.row()
                p = row.operator("thangs.search_invoke", icon='CANCEL')
                p.next_mode = self.next_mode('SEARCH')

                row = layout.row()
                row.scale_y = .001
                row.template_icon_view(
                    wm, "Model", scale=6.5, scale_popup=8, show_labels=True)

                grid = layout.grid_flow(
                    columns=1, even_columns=True, even_rows=True)

                for model in fetcher.pcoll.Model:
                    modelTitle = model[0]
                    label = model[1]

                    cell = grid.column().box()
                    cell.template_icon(icon_value=model[3], scale=7)

                    for x in range(0, len(fetcher.modelInfo)):
                        if fetcher.modelInfo[x][0] == modelTitle:
                            modelURL = fetcher.modelInfo[x][1]
                    cell.operator('wm.url_open', text="%s" % modelTitle).url = modelURL + \
                        "/?utm_source=blender&utm_medium=referral&utm_campaign=blender_extender"

                row = layout.row()
                row.ui_units_y = .9
                row.scale_y = .8
                row.ui_units_x = 20
                row.scale_x = 50

                row.separator(factor=0)

                # pagination = row.column_flow(columns=3, align=True)
                # if fetcher.PageTotal == 1:
                #     pagination.active = False
                # pagination.scale_x = 1
                # pagination.ui_units_y = .1
                # pagination.scale_y = 1.2

                column1 = row.column(align=True)
                if fetcher.PageNumber == 1:
                    column1.active = False

                column1.scale_x = 100
                column1.ui_units_y = .5
                column1.ui_units_x = 100
                column1.scale_y = 1.2

                column2 = row.column(align=True)
                if fetcher.PageNumber == 1:
                    column2.active = False
                column2.scale_x = 10
                column2.ui_units_y = .1
                column2.ui_units_x = 20
                column2.scale_y = 1.2

                column3 = row.column(align=True)
                column3.scale_x = 10
                column3.ui_units_y = .1
                column3.ui_units_x = 20
                column3.scale_y = 1.2

                column4 = row.column(align=True)
                if fetcher.PageNumber == fetcher.PageTotal:
                    column4.active = False

                column4.scale_x = 10
                column4.ui_units_y = .1
                column4.ui_units_x = 20
                column4.scale_y = 1.2

                column5 = row.column(align=True)
                if fetcher.PageNumber == fetcher.PageTotal:
                    column5.active = False

                column5.scale_x = 10
                column5.ui_units_y = .1
                column5.ui_units_x = 20
                column5.scale_y = 1.2

                column1.operator("firstpage.thangs", icon='REW')
                column2.operator("decpage.thangs", icon='PLAY_REVERSE')
                column3.label(text=" "+str(fetcher.PageNumber) +
                              "/"+str(fetcher.PageTotal)+"")
                column4.operator("incpage.thangs", icon='PLAY')
                column5.operator("lastpage.thangs", icon='FF')

                row.separator(factor=0)

                row = layout.row()
                o = row.operator("thangs.search_invoke", icon='CANCEL')
                o.next_mode = self.next_mode('SEARCH')
        else:
            SearchingLayout = self.layout
            SearchingRow = SearchingLayout.row(align=True)
            SearchingRow.label(
                text="Found 0 Models for:")
            SearchingRow = layout.row()
            SearchingRow.label(
                text="“"+bpy.context.scene.thangs_model_search+"” on Thangs")

    def drawSearch(self, context):
        # not searching
        # if len(fetcher.enumItems) > 0:
        # show the results
        #    return
        # show the search box...
        layout = self.layout

        # print(fetcher.enumItems)

        wm = context.window_manager

        col = layout.column(align=True)

        if fetcher.searching:
            col.enabled = False
            SearchingRow = layout.row(align=True)
            SearchingRow.label(
                text="Fetching results for:")
            SearchingRow = layout.row(align=True)
            SearchingRow.label(
                text="'"+bpy.context.scene.thangs_model_search+"'")

        row = col.row()

        row.prop(context.scene, "thangs_model_search")

        row.scale_x = .18
        #row = layout.row()
        #o = row.operator("thangs.search_invoke", icon='VIEWZOOM')
        #o.next_mode = self.next_mode('VIEW')

    def draw(self, context):
        if fetcher.thangs_ui_mode == "VIEW":
            self.drawView(context)
        else:
            self.drawSearch(context)


preview_collections = fetcher.preview_collections


def startSearch(self, value):
    queryText = bpy.context.scene.thangs_model_search
    fetcher.search(query=queryText)


def register():
    from bpy.types import WindowManager
    from bpy.props import (
        StringProperty,
        EnumProperty,
        IntProperty,
        PointerProperty,
    )

    # Added
    WindowManager.Model_page = IntProperty(
        name="Current Page",
        default=0
    )

    WindowManager.Model_dir = StringProperty(
        name="Folder Path",
        subtype='DIR_PATH',
        default=""
    )

    WindowManager.Model = EnumProperty(
        name="",
        description="Click to view all results",
        items=fetcher.enumItems,
    )

    import bpy.utils.previews
    fetcher.pcoll = bpy.utils.previews.new()
    fetcher.icons_dict = bpy.utils.previews.new()
    fetcher.pcoll.Model_dir = ""
    fetcher.pcoll.Model = ()
    # Added
    fetcher.pcoll.Model_page = 0

    fetcher.preview_collections["main"] = fetcher.pcoll
    icon_collections["main"] = icons_dict

    bpy.utils.register_class(THANGS_PT_model_display)
    bpy.utils.register_class(THANGS_OT_search_invoke)
    bpy.utils.register_class(SearchButton)
    bpy.utils.register_class(IncPageChange)
    bpy.utils.register_class(DecPageChange)
    bpy.utils.register_class(ThangsLink)
    bpy.utils.register_class(LastPageChange)
    bpy.utils.register_class(FirstPageChange)

    bpy.types.Scene.thangs_model_search = bpy.props.StringProperty(
        name="",
        description="Search by text or 'Exact Phrase'",
        default="Search",
        update=startSearch
        # update=enter_Search
    )
    print("Finished Register")


def unregister():
    from bpy.types import WindowManager

    del WindowManager.Model

    for pcoll in fetcher.preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    fetcher.preview_collections.clear()
    icon_collections.clear()

    bpy.utils.unregister_class(THANGS_PT_model_display)
    bpy.utils.unregister_class(THANGS_OT_search_invoke)
    bpy.utils.unregister_class(SearchButton)
    bpy.utils.unregister_class(IncPageChange)
    bpy.utils.unregister_class(DecPageChange)
    bpy.utils.unregister_class(ThangsLink)
    bpy.utils.unregister_class(LastPageChange)
    bpy.utils.unregister_class(FirstPageChange)


if __name__ == "__main__":
    register()
