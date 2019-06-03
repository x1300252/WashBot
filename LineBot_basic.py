# -*- coding: UTF-8 -*-

#Python module requirement: line-bot-sdk, flask
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError 
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import DAN, threading, crawl

line_bot_api = LineBotApi('VfYJnNvH+sAqBBb/fAx9nh5Q1QraLNmK20A7gTsRb0yj3kGoIuBihKIEqLtrvhGJgh/oNFacfsr/eeXyVGpu+fXi7gdh4XXTWMPPPFx9xdPXofVkXe20LV32+nzCa8O0S98c4WdhFNXlHR7f8Di6cAdB04t89/1O/w1cDnyilFU=') #LineBot's Channel access token
handler = WebhookHandler('b880d176124e4b2cef879f691b7b5025')  
app = Flask(__name__)

user_list = dict()

@app.route("/", methods=['GET'])
def hello():
    return "HTTPS Test OK."

@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']    # get X-Line-Signature header value
    body = request.get_data(as_text=True)              # get request body as text
    print("Request body: " + body, "Signature: " + signature)
    try:
        handler.handle(body, signature)                # handle webhook body
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    Msg = event.message.text
    print('GotMsg:{}'.format(Msg))
    print('GotMsgfrom:{}'.format(event.source.user_id))

    DAN.push ('washBot_i', Msg, event.source.user_id)

def finish_timer(userID):
    line_bot_api.push_message(userID, TextSendMessage(text='機器使用完畢，請盡快來把衣服拿回去'))
    user_list.pop(userID)

def rest_timer(userID):
    line_bot_api.push_message(userID, TextSendMessage(text='請在3分鐘後來把衣服拿回去'))

def north():
    while True:
        Msg = DAN.pull('wash_north')
        if Msg is not None:
            if Msg[0] != "":
                reply = "北棟：\n"
                w1num = len(crawl.sort_data_with_geo('N1W', crawl.get_status()))
                reply += "1F洗衣機 %d 台"%(w1num)
                if w1num == 0:
                    reply += " 最快%d分鐘後可使用"%(crawl.get_earilest_avaliable('N1W'))

                d1num = len(crawl.sort_data_with_geo('N1D', crawl.get_status()))
                reply += "\n1F烘衣機 %d 台"%(d1num)
                if d1num == 0:
                    reply += " 最快%d分鐘後可使用"%(crawl.get_earilest_avaliable('N1D'))

                
                w9num = len(crawl.sort_data_with_geo('N9W', crawl.get_status()))
                reply += "\n9F洗衣機 %d 台"%(w9num)
                if w9num == 0:
                    reply += " 最快%d分鐘後可使用"%(crawl.get_earilest_avaliable('N9W'))

                
                d9num = len(crawl.sort_data_with_geo('N9D', crawl.get_status()))
                reply += "\n9F烘衣機 %d 台"%(d9num)
                if d1num == 0:
                    reply += " 最快%d分鐘後可使用"%(crawl.get_earilest_avaliable('N9D'))

                line_bot_api.push_message(Msg[0], TextSendMessage(text=reply))
                print (reply)

def south():
    while True:
        Msg = DAN.pull('wash_south')
        if Msg is not None:
            if Msg[0] != "":
                reply = "南棟：\n"
                w1num = len(crawl.sort_data_with_geo('S1W', crawl.get_status()))
                reply += "1F洗衣機 %d 台"%(w1num)
                if w1num == 0:
                    reply += " 最快%d分鐘後可使用"%(crawl.get_earilest_avaliable('S1W'))

                d1num = len(crawl.sort_data_with_geo('S1D', crawl.get_status()))
                reply += "\n1F烘衣機 %d 台"%(d1num)
                #if d1num == 0:
                    #reply += " 最快%d分鐘後可使用"%(crawl.get_earilest_avaliable('S1D'))

                
                w10num = len(crawl.sort_data_with_geo('S10W', crawl.get_status()))
                reply += "\n10F洗衣機 %d 台"%(w10num)
                if w10num == 0:
                    reply += " 最快%d分鐘後可使用"%(crawl.get_earilest_avaliable('S10W'))

                
                d10num = len(crawl.sort_data_with_geo('S10D', crawl.get_status()))
                reply += "\n10F烘衣機 %d 台"%(d10num)
                if d10num == 0:
                    reply += " 最快%d分鐘後可使用"%(crawl.get_earilest_avaliable('S10D'))

                line_bot_api.push_message(Msg[0], TextSendMessage(text=reply))
                print (reply)

def register():
    while True:
        Msg = DAN.pull('wash_register')
        if Msg is not None:
            if Msg[0] != "":
                if len(Msg[0][0])==0:
                    line_bot_api.push_message(Msg[0][1], TextSendMessage(text='請輸入你正在使用的機器編號'))
                else:
                    data = crawl.sort_data_with_geo(Msg[0][0], crawl.get_data(crawl.url))
                    if len(data) == 1:
                        if (crawl.get_duration(Msg[0][0]) == 0):
                            line_bot_api.push_message(Msg[0][1], TextSendMessage(text='請開始使用後再輸入機器編號'))
                        else:
                            user_list[Msg[0][1]] = Msg[0][0]
                            line_bot_api.push_message(Msg[0][1], TextSendMessage(text='你正在使用的機器為%s，使用完畢會提醒你'%Msg[0][0]))
                        
                            timer = threading.Timer(10, finish_timer, args=(Msg[0][1],))#crawl.get_duration(Msg[0][0])*60
                            timer.daemon = True
                            timer.start()

                            timer = threading.Timer(5, rest_timer, args=(Msg[0][1],))#crawl.get_duration(Msg[0][0])*60-180
                            timer.daemon = True
                            timer.start()
                    else:
                        line_bot_api.push_message(Msg[0][1], TextSendMessage(text='請輸入正確的機器編號'))
                print ("我目前正在使用 "+str(Msg[0]))


def my_status():
    while True:
        Msg = DAN.pull('wash_my_status')
        if Msg is not None:
            if Msg[0] != "":
                if Msg[0] in user_list:
                    rest = crawl.get_duration(user_list[Msg[0]])
                    if rest > 0:
                        reply = "還剩%d分鐘就完成了"%rest
                    else:
                        reply = "無人使用本機器"
                    line_bot_api.push_message(Msg[0], TextSendMessage(text=reply))
                    print ("我的使用狀態 "+reply)
                else:
                    line_bot_api.push_message(Msg[0], TextSendMessage(text='你沒有正在使用的機器'))
                    print ("你沒有正在使用的機器")

   
if __name__ == "__main__":
    ServerURL = 'http://140.113.199.188:9999' #with no secure connection
    Reg_addr = "final" #if None, Reg_addr = MAC address

    DAN.profile['dm_name']='washBot'
    DAN.profile['df_list']=['washBot_i', 'wash_north', 'wash_south', 'wash_my_status', 'wash_register']
    DAN.profile['d_name']= None # None for autoNaming
    DAN.device_registration_with_retry(ServerURL, Reg_addr)
    
    tlist = [north, south, my_status, register]

    for func in tlist:
        t = threading.Thread(target=func)
        t.daemon = True     # this ensures thread ends when main process ends
        t.start()
    
    app.run('127.0.0.1', port=32768, threaded=True, use_reloader=False)

    

