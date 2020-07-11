import maya.cmds as cmds
import maya.OpenMaya as openMaya

filename = ""

def seffile():
    global filename
    filename = cmds.fileDialog(mode=1)
    cmds.text(place_info, e=True, label=filename)

def worldSpaceToImageSpace(camera, worldPoint):
    resWidth = cmds.getAttr('defaultResolution.width')
    resHeight = cmds.getAttr('defaultResolution.height')
    
    selList = openMaya.MSelectionList()
    selList.add(camera)
    dagPath = openMaya.MDagPath()
    selList.getDagPath(0, dagPath)
    dagPath.extendToShape()
    camInvMtx = dagPath.inclusiveMatrix().inverse()
    
    fnCam = openMaya.MFnCamera(dagPath)
    mFloatMtx = fnCam.projectionMatrix()
    projMtx = openMaya.MMatrix(mFloatMtx.matrix)
    
    mPoint = openMaya.MPoint(worldPoint[0],worldPoint[1],worldPoint[2]) * camInvMtx * projMtx;
    x = (mPoint[0] / mPoint[3] / 2 + 0.5) * resWidth
    y = (mPoint[1] / mPoint[3] / 2 + 0.5) * resHeight
    
    y = resHeight - y
    return [x,y]

def ptr_main():
    cmds.text(error_info, e=True, label="")
    selected_cam = cmds.optionMenu(cam_list, q=True, value=True)
    
    if filename != "":    
        sTime = cmds.playbackOptions(q=True, minTime=True)
        eTime = cmds.playbackOptions(q=True, maxTime=True)
        
        data_buffer = []
        
        TGT_item = cmds.ls(selection=True)
        for i in range(int(sTime), int(eTime)):
            cmds.currentTime(i)
            data_buffer.append(cmds.currentTime(query=True, update=False))
            TGT_POSITION = cmds.pointPosition(TGT_item, world=True)
            t1 = worldSpaceToImageSpace(selected_cam, TGT_POSITION)
            data_buffer.append(t1[0])
            data_buffer.append(t1[1])
            
        with open(filename, 'w') as f:
            for t in data_buffer:
                f.write("%s\n" %str(t))
    else:
        cmds.text(error_info, e=True, label="<h1>Please select file</h1>")

window = cmds.window(title="Pointer", width=300)
cmds.columnLayout()

cam_list = cmds.optionMenu(label="camera list", width=300, height=20)
for item in cmds.ls(cameras=True):
    cmds.menuItem(label=item)
    
cmds.text(label='<h3><br>カメラを指定した後出力先を指定、対象のオブジェクトを選択し、<br>Exportをおしてください。<h3>', align="left")
cmds.rowLayout(numberOfColumns=2, columnWidth2=(100, 200))
cmds.button(label="select file", command="seffile()", width=100)
place_info = cmds.text(label='Not selected')
cmds.setParent('..')
error_info = cmds.text(label='')
cmds.button(label='Export', command="ptr_main()", width=100)
cmds.showWindow(window)
