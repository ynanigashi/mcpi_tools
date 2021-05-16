'''
20210424
todo
#バク修正
#　方向が違う
#リファクタリング
機能追加
　Y軸も読み込む

# 自分の周りの情報をファイルに書き出す
# ファイルからデータを読んでオブジェクトを生成
ファイルに書き出した情報を指定の名前にリネーム
移動をそれっぽくする
一定エリアのブロックを壊す？消し去る？
壊すにできないものか？
設計図に従ってブロックを作る


20210508
X東とZ南
      N
     -Z
W -X ** +X E
     +Z
      S
'''
import sys,time
from enum import Enum
from mcpi import minecraft, block, entity, vec3
import pickle

mc = minecraft.Minecraft.create()
PICKLE_FILE = './temp.pickle'

class Way(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

#プレイヤーの向いている方角を出す
def get_way(entity):
    direction = entity.getDirection()
    if abs(direction.x) > abs(direction.z):
        if direction.x > 0: return Way.EAST
        else: return Way.WEST
    else:
        if direction.z > 0: return Way.SOUTH
        else: return Way.NORTH

#方向に基づき相対位置を回転させる
def rotate_vec(vec, way):
    if way == Way.EAST: None
    elif way == Way.SOUTH: vec.rotateRight()
    elif way == Way.WEST: 
        vec.rotateRight()
        vec.rotateRight()
    elif way == Way.NORTH: vec.rotateLeft()
    return vec

def generate_wall(size):
    #プレイヤー位置を取得
    player_pos = mc.player.getPos()

    #プレイヤーの向きを出す
    way = get_way(mc.player)

    #ブロックの相対位置のリストを作る
    vecs = [vec3.Vec3(5,i,j) for i in range(0,size)
                                for j in range(int(-size//2), int(size//2))]

    #現在位置に相対位置を足しブロックを作る
    for vec in vecs:
        vec = rotate_vec(vec, way)
        vec += player_pos
        mc.setBlock(vec.x,vec.y,vec.z, block.DIAMOND_BLOCK)

def move_front(distance):
    #mc.postToChat(distance)
    player_dir = mc.player.getDirection()
    start_pos = mc.player.getPos()
    next_pos = start_pos.clone()
    player_dir.y = 0
    goal_pos = start_pos + player_dir * distance
    dist_vec = goal_pos - start_pos
    start_time = time.time()
    interval = 3 
    while True:
        elapsed = time.time() - start_time
        if elapsed >= interval:
            mc.player.setPos(goal_pos)
            break
        next_pos = start_pos + dist_vec * (elapsed/interval)
        #mc.postToChat( mc.getBlock(next_pos))
        if mc.getBlock(next_pos) in [0,31,78,79]:
            mc.player.setPos(next_pos)
        else:
            mc.getBlock(next_pos)
            break
        time.sleep(0.017)

# class  CuboidData:
#     def __init__(self, size, blocks):
#         self.size = size
#         self.blocks = blocks

def get_block_info():
#自分のいるセルを取得
    player_tpos = mc.player.getTilePos()
    #mc.postToChat(player_tpos)

    #対象範囲の２点を取得
    area_size = vec3.Vec3(1, 2, 3)
    v1 = vec3.Vec3(1, 0, -(area_size.z//2))
    v2 = v1 + area_size - vec3.Vec3(1, 1, 1)
    way = get_way(mc.player)
    v1 = rotate_vec_fromto(v1, Way.EAST, way)
    v2 = rotate_vec_fromto(v2, Way.EAST, way)

    start = player_tpos + vec3.Vec3(min(v1.x, v2.x), v1.y, min(v1.z, v2.z))
    end = player_tpos + vec3.Vec3(max(v1.x, v2.x), v2.y, max(v1.z, v2.z))
    
    #Block情報を取得する
    blocks = mc.getBlocksWithNBT(*start, *end)

    for block in blocks:
        mc.postToChat("{}, {}, {}".format(block.id, block.data, str(block.nbt)))


def scan_area():
    #自分のいるセルを取得
    player_tpos = mc.player.getTilePos()
    #mc.postToChat(player_tpos)

    #対象範囲の２点を取得
    area_size = vec3.Vec3(10, 40, 10)
    v1 = vec3.Vec3(1, -(area_size.y//2), -(area_size.z//2))
    v2 = v1 + area_size - vec3.Vec3(1, 1, 1)
    way = get_way(mc.player)
    v1 = rotate_vec_fromto(v1, Way.EAST, way)
    v2 = rotate_vec_fromto(v2, Way.EAST, way)

    start = player_tpos + vec3.Vec3(min(v1.x, v2.x), v1.y, min(v1.z, v2.z))
    end = player_tpos + vec3.Vec3(max(v1.x, v2.x), v2.y, max(v1.z, v2.z))
    
    #Block情報を取得する
    blocks = mc.getBlocksWithNBT(*start, *end)
    #mc.postToChat(blocks)
    
    pos_block_list = []
    i = 0
    #blocksに位置情報を追加
    for y in range(0, area_size.y):
        for x in range(0, area_size.x):
            for z in range(0, area_size.z):
                block_pos = start + vec3.Vec3(x, y, z)
                block = mc.getBlockWithData(*block_pos)
                relative_pos = block_pos - player_tpos
                relative_pos = rotate_vec_fromto(relative_pos, way, Way.EAST)
                pos_block_list.append((relative_pos, block))
                i += 1
    #mc.postToChat(pos_block_list)
    
    file_path = PICKLE_FILE
    with open(file_path,'wb') as f:
        pickle.dump(pos_block_list, f)

def paste_area():
    file_path = PICKLE_FILE
    with open(file_path, 'rb') as f:
        pos_block_list = pickle.load(f)
    
    #mc.postToChat(pos_block_list)
    
    #自分のいるセルを取得
    player_tpos = mc.player.getTilePos()
    # mc.postToChat(player_tpos)
    way = get_way(mc.player)
    
    #Pickleの情報をセット
    for block_pos, block in pos_block_list:
        pos = rotate_vec_fromto(block_pos, Way.EAST, way)
        pos += player_tpos
        mc.setBlockWithNBT(*pos, block.id, block.data, str(block.nbt))

def clear_area():
    #自分のいるセルを取得
    player_tpos = mc.player.getTilePos()
    #mc.postToChat(player_tpos)

    #対象範囲の２点を取得
    area_size = vec3.Vec3(50, 20, 50)
    v1 = vec3.Vec3(1, 0, -(area_size.z//2))
    v2 = v1 + area_size - vec3.Vec3(1, 1, 1)
    way = get_way(mc.player)
    v1 = rotate_vec_fromto(v1, Way.EAST, way)
    v2 = rotate_vec_fromto(v2, Way.EAST, way)

    start = player_tpos + vec3.Vec3(min(v1.x, v2.x), v1.y, min(v1.z, v2.z))
    end = player_tpos + vec3.Vec3(max(v1.x, v2.x), v2.y, max(v1.z, v2.z))
    
    #Blockをセットする
    mc.setBlocks(*start, *end, block.AIR)


def generate(filename):
    class Mode(Enum):
        MOVE = 0
        BLOCK = 1

    #mc.postToChat(f"filename: {filename}")
    with open('./' + filename, 'r') as f:
        src = f.read()

    player = mc.player.getTilePos()
    cur = vec3.Vec3(0, 0, 0)
    mode = Mode.MOVE
    block_id = block.AIR
    block_data = 0
    way = get_way(mc.player)

    def put_block():
        if mode == Mode.BLOCK:
            mc.setBlockWithNBT(*(player + cur), block_id, block_data, '')

    def parse_int(s):
        try:
            return int(s)
        except Exception as e:
            mc.postToChat(f"error: invalid token {s}")
            raise e

    def move(cur, way, n):
        step = rotate_vec_fromto(vec3.Vec3(1, 0, 0), Way.EAST, way)
        for i in range(0, n):
            put_block()
            # if mode == Mode.BLOCK:
                # mc.setBlock(*(player + cur), block_id)
            cur += step

    # トークンを頭からpopしていく
    tokens = src.split()[::-1]
    while len(tokens) > 0:
        token = tokens.pop()
        if token[0] == 'M':
            mode = Mode.MOVE
            #mc.postToChat(f"block_id: {block_id}")
        elif token[0] == 'P':
            if ',' in token[1:]:
                _block_id, _data = token[1:].split(',')
                #mc.postToChat(f"val: {_block_id} / {_data}")
                block_id = parse_int(_block_id)
                block_data = parse_int(_data)
            else:
                block_id = parse_int(token[1:])
                block_data = 0
            mode = Mode.BLOCK
            put_block()
            #mc.postToChat(f"block_id: {block_id}")
        elif token[0] == 'F':
            n = parse_int(token[1:])
            move(cur, way, n)
        elif token[0] == 'B':
            n = parse_int(token[1:])
            move(cur, Way((way.value + 2) % 4), n)
        elif token[0] == 'L':
            n = parse_int(token[1:])
            move(cur, Way((way.value + 3) % 4), n)
        elif token[0] == 'R':
            n = parse_int(token[1:])
            move(cur, Way((way.value + 1) % 4), n)
        elif token[0] == 'U':
            n = parse_int(token[1:])
            for _ in range(n):
                cur += vec3.Vec3(0, 1, 0)
                put_block()
        elif token[0] == 'D':
            n = parse_int(token[1:])
            for _ in range(n):
                cur += vec3.Vec3(0, -1, 0)
                put_block()
        else:
            continue

def build_stairs(num):
    player_pos = mc.player.getTilePos()
    way = get_way(mc.player)
    step = rotate_vec_fromto(vec3.Vec3(1, 0, 0), Way.EAST, way)

    stair_data = {
        Way.WEST: 1,
        Way.EAST: 0,
        Way.NORTH: 3,
        Way.SOUTH: 2,
    }[way]
    #mc.postToChat(f'way: {way}, step: {step}, stair_data: {stair_data}')
    start_pos = player_pos + step * 1
    for max_level in range(num+1):
        for lv in range(max_level):
            pos = start_pos + (step * max_level) + vec3.Vec3(0, lv, 0)
            if lv+1 < max_level:
                mc.setBlock(*pos, block.WOOD_PLANKS.id)
            else:
                mc.setBlockWithNBT(*pos, block.STAIRS_WOOD.id, stair_data, '')
        for lv in range(max_level, num+1):
            pos = start_pos + (step * max_level) + vec3.Vec3(0, lv, 0)
            mc.setBlock(*pos, block.AIR.id)




def start(args):
    #mc.postToChat(args)
    if len(args) <= 0:
        mc.postToChat("set arguments!")
        exit()
 
    if args[0] == "wall":
        try:
            size = int(args[1])
        except Exception:
            size = 5
        generate_wall(size)

    elif args[0] == "walk":
        try:
            distance = int(args[1])
        except Exception:
            distance = 5
        before = time.time()
        move_front(distance)
        after = time.time()
        #mc.postToChat(after - before)

    elif args[0] == "scan":
        scan_area()

    elif args[0] == "paste":
        paste_area()

    elif args[0] == "clear":
        clear_area()

    elif args[0] == "generate":
        if len(args) > 1:
            filename = args[1]
            generate(filename)
        else:
            mc.postToChat("Filename is required")
            return

    elif args[0] == "stairs":
        if len(args) > 1:
            num = int(args[1])
            build_stairs(num)
        else:
            mc.postToChat("Stair level is required")
            return

    elif args[0] == "test":
        get_block_info()


def rotate_vec_fromto(vec, way_from, way_to):
    diff = (4 + (way_to.value - way_from.value)) % 4
    if diff == 1:
        vec.rotateRight()
    elif diff == 2:
        vec.rotateRight()
        vec.rotateRight()
    elif diff == 3:
        vec.rotateLeft()
    return vec



# for i in range(0, 10):
#     for j in range(0, 10):
#         mc.setBlock((player_pos.x+j, player_pos.y+i, player_pos.z, block.GLOWING_OBSIDIAN))


if __name__ == "__main__":
    # try:
        start(sys.argv[1:])
    # except Exception as e:
        # mc.postToChat(f"exception: {e}")