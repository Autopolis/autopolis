Cversion = '1.0.0'

"""
 Autopollism contracts
"""
from hashgard.interop.System.Storage import Get, Put
from hashgard.interop.System.Runtime import GetTxSender
from hashgard.builtins import state
from hashgard.interop.System.Contract import Register
from hashgard.interop.System.String import IntToStr

# this address is APT token contract address
APTContractAdress = 'contracte298d012e0fae9d887c95c167d3220f6b26cfdbe'


OWNER = 'gard1etpr86c45q85xjk8m4fp0qqzenpmn8j3a5vhzd'


KEY_OWNER = "owner"

KEY_TOTAL_SCORE = "total_score"
KEY_ADDRESS_LIST = "address_list"


REWARD_POOL = 1000000000

GRANT_RATIO = 3

# game start time 2019/9/1/00:00
GAME_START_TIME = 1567267200
GAME_START_ROUND = 0

# game time for a round: a week
GAME_TIME_FOR_A_ROUND = 3600 * 24 * 7


def main(operation, args):
    if operation == 'init':
        return init()
    if operation == 'owner':
        return owner()
    if operation == 'uploadData':
        if len(args) != 4:
            return False
        return upload_data(args[0], args[1], args[2], args[3])
    if operation == 'grantReward':
        return grant_reward(args[0])

    return False


def APTContract(params):
    return Register(APTContractAdress, params)


def init():
    # check if contract inited
    if Get(KEY_OWNER):
        return False

    Put(KEY_OWNER, OWNER)

    return True


def getRound(time):
    return ((time - GAME_START_TIME) - (time - GAME_START_TIME) % GAME_TIME_FOR_A_ROUND) / GAME_TIME_FOR_A_ROUND


# --------------------------------------------- #
# -------------- query functions -------------- #
# --------------------------------------------- #
def owner():
    return Get(KEY_OWNER)


# --------------------------------------------- #
# -------------- 1. upload data functions ----- #
# --------------------------------------------- #
def upload_data(score, km, data, time):
    # 1.1 upload [score, km, data, time]  for a round-user
    round = getRound(time)
    addr = GetTxSender()
    roundUserKey = IntToStr(round) + addr

    record = [score, km, data, time]

    recordList = Get(roundUserKey)
    if len(recordList) == 0:
        Put(roundUserKey, [record])
    else:
        recordList[len(recordList)] = record
        Put(roundUserKey, recordList)

    # 1.2 upload total score
    totalScore = Get(KEY_TOTAL_SCORE)
    Put(KEY_TOTAL_SCORE, totalScore+score)

    # 1.3 upload address list for a round
    addressList = Get(round)
    if len(addressList) == 0:
        Put(round,[addr])
    else:
        is_existed = False
        for a in addressList:
            if a == addr:
                is_existed = True
                break
        if not is_existed:
            addressList[len(addressList)] = addr
            Put(round, addressList)
    return True


# --------------------------------------------- #
# -------------- 2. caculate reward functions - #
# --------------------------------------------- #
def cal_reward(address, round):
    roundUserKey = IntToStr(round) + address
    recordList = Get(roundUserKey)
    score = 0
    for record in recordList:
        score += record[0]

    totalScore = Get(KEY_TOTAL_SCORE)
    reward = REWARD_POOL*score**GRANT_RATIO/totalScore
    return reward


# --------------------------------------------- #
# -------------- 3. grant reward functions ---- #
# --------------------------------------------- #
def approve(sender, spender, amount):
    # call APTContract approve
    param = state('string:approve', '[string:', sender, 'string:', spender, 'int:', amount, ']')
    APTContract(param)
    return True


def grant_reward(round):
    sender = GetTxSender()
    addressList = Get(KEY_ADDRESS_LIST)
    for a in addressList:
        reward = cal_reward(a, round)
        approve(sender, a, reward)
    return True
