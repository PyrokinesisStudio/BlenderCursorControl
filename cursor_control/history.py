# -*- coding: utf-8 -*-
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####



"""
  TODO:

      IDEAS:

      LATER:

      ISSUES:
          Bugs:
              Seg-faults when unregistering addon...
          Mites:
            * History back button does not light up on first cursor move.
              It does light up on the second, or when mouse enters the tool-area
            * Switching between local and global view triggers new cursor position in history trace.
            * Each consecutive click on the linex operator triggers new cursor position in history trace.
                 (2011-01-16) Was not able to fix this because of some strange script behaviour
                              while trying to clear linexChoice from addHistoryLocation

      QUESTIONS:



"""



import bpy
import bgl
import blf
import math
from mathutils import Vector, Matrix
from mathutils import geometry
from misc_utils import *
from constants_utils import *
from cursor_utils import *
from ui_utils import *


PRECISION=4


class CursorHistoryData(bpy.types.PropertyGroup):
    # History tracker
    historyEnabled = [0]
    historyDraw = bpy.props.BoolProperty(description="Draw history trace in 3D view",default=1)
    historyDepth = 144
    historyWindow = 6
    historyPosition = [-1] # Integer must be in a list or else it can not be written to
    historyLocation = []
    #historySuppression = [False] # Boolean must be in a list or else it can not be written to

    def addHistoryLocation(self, l):
        if(self.historyPosition[0]==-1):
            self.historyLocation.append(l.copy())
            self.historyPosition[0]=0
            return
        if(l==self.historyLocation[self.historyPosition[0]]):
            return
        #if self.historySuppression[0]:
            #self.historyPosition[0] = self.historyPosition[0] - 1
        #else:
            #self.hideLinexChoice()
        while(len(self.historyLocation)>self.historyPosition[0]+1):
            self.historyLocation.pop(self.historyPosition[0]+1)
        #self.historySuppression[0] = False
        self.historyLocation.append(l.copy())
        if(len(self.historyLocation)>self.historyDepth):
            self.historyLocation.pop(0)
        self.historyPosition[0] = len(self.historyLocation)-1
        #print (self.historyLocation)

    #def enableHistorySuppression(self):
        #self.historySuppression[0] = True

    def previousLocation(self):
        if(self.historyPosition[0]<=0):
            return
        self.historyPosition[0] = self.historyPosition[0] - 1
        CursorAccess.setCursor(self.historyLocation[self.historyPosition[0]].copy())

    def nextLocation(self):
        if(self.historyPosition[0]<0):
            return
        if(self.historyPosition[0]+1==len(self.historyLocation)):
            return
        self.historyPosition[0] = self.historyPosition[0] + 1
        CursorAccess.setCursor(self.historyLocation[self.historyPosition[0]].copy())



class VIEW3D_OT_cursor_previous(bpy.types.Operator):
    '''Previous cursor location'''
    bl_idname = "view3d.cursor_previous"
    bl_label = "Previous cursor location"
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_history
        cc.previousLocation()
        return {'FINISHED'}



class VIEW3D_OT_cursor_next(bpy.types.Operator):
    '''Next cursor location'''
    bl_idname = "view3d.cursor_next"
    bl_label = "Next cursor location"
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_history
        cc.nextLocation()
        return {'FINISHED'}



#class VIEW3D_OT_cursor_history_show(bpy.types.Operator):
    #'''Show cursor trace'''
    #bl_idname = "view3d.cursor_history_show"
    #bl_label = "Show cursor trace"
    #bl_options = {'REGISTER'}

    #def modal(self, context, event):
        #return {'FINISHED'}

    #def execute(self, context):
        #cc = context.scene.cursor_history
        #cc.historyDraw = True
        #BlenderFake.forceRedraw()
        #return {'FINISHED'}



#class VIEW3D_OT_cursor_history_hide(bpy.types.Operator):
    #'''Hide cursor trace'''
    #bl_idname = "view3d.cursor_history_hide"
    #bl_label = "Hide cursor trace"
    #bl_options = {'REGISTER'}

    #def modal(self, context, event):
        #return {'FINISHED'}

    #def execute(self, context):
        #cc = context.scene.cursor_history
        #cc.historyDraw = False
        #BlenderFake.forceRedraw()
        #return {'FINISHED'}



class VIEW3D_OT_cursor_history_toggledraw(bpy.types.Operator):
    '''Toggle cursor trace'''
    bl_idname = "view3d.cursor_history_toggledraw"
    bl_label = "Toggle cursor trace"
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        return {'FINISHED'}

    def execute(self, context):
        cc = context.scene.cursor_history
        cc.historyDraw = not cc.historyDraw
        BlenderFake.forceRedraw()
        return {'FINISHED'}



class VIEW3D_PT_cursor_history(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Cursor History"
    bl_default_closed = True

    initDone = False
    
    @classmethod
    def poll(cls, context):

        # Setup (if not done)
        if not VIEW3D_PT_cursor_history.initDone:
            sce = context.scene
            if context.area.type == 'VIEW_3D':
                for reg in context.area.regions:
                    if reg.type == 'WINDOW':
                        # Register callback for drawing trace
                        reg.callback_add(cursor_history_draw,(cls,context),'POST_PIXEL')
                        # Start tracker
                        if bpy.ops.view3d.cursor_tracker.poll():
                            bpy.ops.view3d.cursor_tracker()
                        # Flag success
                        VIEW3D_PT_cursor_history.initDone = True
                        #print ("Cursor History draw-callback registered")
            else:
                print("View3D not found, cannot run operator")

        #if not VIEW3D_OT_CursorTracker.inhibit:
            #print ("Not inhibited")
            #cc = context.scene.cursor_history
            #cc.addHistoryLocation(CursorAccess.getCursor())
        #BlenderFake.forceRedraw()
        
        # Display panel in object or edit mode.
        if (context.area.type == 'VIEW_3D' and
            (context.mode.startswith('EDIT')
            or context.mode == 'OBJECT')):
            cc = context.scene.cursor_history.historyEnabled[0] = 1
            return 1
            
        cc = context.scene.cursor_history.historyEnabled[0] = 0
        return 0

    def draw_header(self, context):
        layout = self.layout
        cc = context.scene.cursor_history
        if cc.historyDraw:
            GUI.drawIconButton(True, layout, 'RESTRICT_VIEW_OFF', "view3d.cursor_history_toggledraw", False)
        else:
            GUI.drawIconButton(True, layout, 'RESTRICT_VIEW_ON' , "view3d.cursor_history_toggledraw", False)

    def draw(self, context):
        layout = self.layout
        sce = context.scene
        cc = context.scene.cursor_history

        row = layout.row()
        row.label("Navigation: ")
        GUI.drawIconButton(cc.historyPosition[0]>0, row, 'PLAY_REVERSE', "view3d.cursor_previous")
        #if(cc.historyPosition[0]<0):
            #row.label("  --  ")
        #else:
            #row.label("  "+str(cc.historyPosition[0])+"  ")
        GUI.drawIconButton(cc.historyPosition[0]<len(cc.historyLocation)-1, row, 'PLAY', "view3d.cursor_next")

        row = layout.row()
        col = row.column()
        col.prop(CursorAccess.findSpace(), "cursor_location")

  

def cursor_history_draw(cls,context):
    cc = context.scene.cursor_history

    draw = 0
    if hasattr(cc, "historyDraw"):
        draw = cc.historyDraw
    if hasattr(cc, "historyEnabled"):
        if(not cc.historyEnabled[0]):
            draw = 0

    if(draw):
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glShadeModel(bgl.GL_FLAT)
        alpha = 1-PHI_INV
        # History Trace
        if cc.historyPosition[0]<0:
            return
        bgl.glBegin(bgl.GL_LINE_STRIP)
        ccc = 0
        p2 = Vector(CursorAccess.getCursor())
        pp = None
        pn = None
        for iii in range(cc.historyWindow+1):
            ix_rel = iii - int(cc.historyWindow / 2)
            ix = cc.historyPosition[0] + ix_rel
            if(ix<0 or ix>=len(cc.historyLocation)):
                continue
            ppp = region3d_get_2d_coordinates(context, cc.historyLocation[ix])
            if(ix_rel==-1):
                pp = Vector(cc.historyLocation[ix])
            if(ix_rel==1):
                pn = Vector(cc.historyLocation[ix])
            if(ix_rel<=0):
                bgl.glColor4f(0, 0, 0, alpha)
            else:
                bgl.glColor4f(1, 0, 0, alpha)
            bgl.glVertex2f(ppp[0], ppp[1])
            ccc = ccc + 1
        bgl.glEnd()
        
        # Distance of last step
        y=10
        if(pn):
            bgl.glColor4f(1, 0, 0, PHI_INV)
            location=region3d_get_2d_coordinates(context, p2)
            blf.size(0, 10, 72)  # Prevent font size to randomly change.
            d = (p2-pn).length
            blf.position(0, location[0]+10, location[1]+y, 0)
            blf.draw(0, str(round(d,PRECISION)))
            y = y + 10;
        if(pp):
            bgl.glColor4f(0, 0, 0, PHI_INV)
            location=region3d_get_2d_coordinates(context, p2)
            blf.size(0, 10, 72)  # Prevent font size to randomly change.
            d = (p2-pp).length
            blf.position(0, location[0]+10, location[1]+y, 0)
            blf.draw(0, str(round(d,PRECISION)))




class VIEW3D_OT_CursorTracker(bpy.types.Operator):
    bl_idname = "view3d.cursor_tracker"
    bl_label = "Track 3D cursor movement"
    bl_options = {'REGISTER'}

    execute = True
    inhibit = False

    #def __init__(self):
        #pass

    #def __del__(self):
        #pass

    @classmethod
    def poll(cls, context):
        return VIEW3D_OT_CursorTracker.execute

    def execute(self, context):
        VIEW3D_OT_CursorTracker.execute = False
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        #if event.type == 'LEFTMOUSE':
            #if event.value == 'PRESS':
                #VIEW3D_OT_CursorTracker.inhibit = True
            #if event.value == 'RELEASE':
                #VIEW3D_OT_CursorTracker.inhibit = False
        #print (event.type+" "+event.value)
        #if VIEW3D_OT_CursorTracker.inhibit:
            #return {'PASS_THROUGH'}

        VIEW3D_OT_CursorTracker.track(context)

        return {'PASS_THROUGH'}
        
    @classmethod
    def track(cls, context):
        cc = context.scene.cursor_history
        cc.addHistoryLocation(CursorAccess.getCursor())
        VIEW3D_OT_CursorTracker.inhibit = False
        BlenderFake.forceRedraw()

