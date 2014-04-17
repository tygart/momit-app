__version__ = '0.2.4'

from time import sleep
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
import json
from os.path import join, exists
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.graphics import Color, BorderImage
from kivy.core.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.atlas import Atlas
import lxml.html
import requests
from functools import partial
import webbrowser
from threading import Thread


class RootWindow(BoxLayout):

    def __init__(self,**kwargs):
        super(RootWindow, self).__init__(**kwargs)
        self.save_path= None
        self.req = None
        self.req_app = None
        self.req2 = [{'msg':'','name':'','time':'','url':'','len':0} for _ in range(0, 50, 1)]
        self.req2_app = [{'msg':'','name':'','time':'','url':'','len':0} for _ in range(0, 50, 1)]
        self.user = self.ids.usern
        self.passwor = self.ids.passw
        self.data2 = {'user':'','pass':''}


    def load_notes(self):
        if not exists(self.notes_fn):
            return
        with open(self.notes_fn, 'rb') as fd:
            data1 = json.load(fd)
        self.data2 = data1
        print(self.save_path)
        print(self.data2)
        self.user.text = self.data2['user']
        self.passwor.text = self.data2['pass']


    def save_notes(self):

        self.ids.loading.anim_load()
        Window.release_all_keyboards()
        self.data2['user']=self.user.text
        self.data2['pass']=self.passwor.text
        Clock.schedule_once(self.login_m,1)


    def unverified(self):

        label = self.ids.verified
        label.text = 'unverified'


    def verified(self):

        label = self.ids.verified
        label.text = 'verified'


    def login_m(self,post_m=None,*args):
        print('called login check')
        user = self.user.text
        password = self.passwor.text

        s = requests.Session()
        s.keep_alive = False
        url = 'http://www.momit.org'
        a = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount(url, a)

        try:
            result = s.get(url, timeout=10)
        except requests.exceptions.ConnectionError as e:
            print(e)
            text='App: time and money wasted! :( Connection error.'
            Clock.schedule_once(partial(self._on_error, text),1)
            return
        except requests.exceptions.HTTPError as e:
            print(e)
            text='App: time and money wasted! :( HTTP error.'
            Clock.schedule_once(partial(self._on_error),text,1)
            return

        except requests.exceptions.Timeout as e:
            print(e)
            text='App: time and money wasted! :( Timeout error.'
            Clock.schedule_once(partial(self._on_error,text),1)
            return

        except requests.exceptions.RequestException as e:
            print(e)
            text='App: time and money wasted! :( Catastrophic error.'
            Clock.schedule_once(partial(self._on_error,text),1)
            return

        doc = lxml.html.fromstring(result.text)
        
        fields=[]
        for a in doc.xpath('//*[@id="form-login"]/input'):  
            fields+=[a.name]       
            fields+=[a.value]
        

        login_data={'Submit':'Login', 'username': user, 'passwd': password, 'task': 'login','option': 'com_user',
                        'silent': 'true', 'return': fields[-3], fields[-2]: '1'}
        result2 = s.post(url, data=login_data)

        doc2 = lxml.html.fromstring(result2.text)

        output2 = doc2.xpath('//*[@id="leftcol"]/div/div[1]/div/div[2]/h3/text()') 
        if out_test == 'Guild Chat Jr.':
            self.verified()
            print('login passed')
            self.ids.postname.text = doc2.xpath('//*[@id="chatForm"]/p/label[1]/em/text()')[0]+':'
            
            with open(self.notes_fn, 'wb') as fd:
                json.dump(self.data2, fd)
            

            if isinstance(post_m, str):
                fields=[]
                print('post called')
                for a in doc2.xpath('//*[@id="form-login"]/input'): 
                    fields+=[a.name]            
                    fields+=[a.value]

                post_name=doc2.xpath('//*[@id="chatForm"]/p/label[1]/em/text()')
                
                jal_id=doc2.xpath('//*[@id="jal_lastID"]/@value')
                
                post_data={'submit':'Send', 'shoutboxname':post_name[0], 'shoutboxurl':'http://',
                           'chatbarText': post_m, 'jal_lastID':jal_id[0], 'shout_no_js':'true'}
                result3 = s.post(url, data=post_data)

                doc3 = lxml.html.fromstring(result3.text)
                self.get_data_app(doc3)
            else:
                print('get called')
                self.get_data_app(doc2)

        elif out_test == 'Login/Logout':
            self.unverified()
            print('login failed')
            self.ids.postname.text = 'Login info. needed.'
            print(self.data2)
            with open(self.notes_fn, 'wb') as fd:
                json.dump(self.data2, fd)
            self.get_data()
        else:
            print('no response to login')
            

    def twss(self):
        self.ids.post.insert_text('that\'s what she said', from_undo=False)


    def http(self):
        self.ids.post.insert_text('http://', from_undo=False)


    def _on_error(self, requ, text=None, *args):
        print('login failure')
        with open(self.notes_fn, 'wb') as fd:
                json.dump(self.data2, fd)
        print(text)
        if not isinstance(text, str):
            text = 'App: time and money wasted! :( connection error.'
        data4={ 'entry': 0, 'msg': text,
                'url': 'na', 'time': '0 minutes'}
        self.req2 = self.translate_unicode([data4])
        self.seperate_name(self.req2)
        self.add_hyperlinks(self.req2)
        self.build_board()


    @property
    def notes_fn(self):
        return join(self.save_path, 'momit.json')


    def submit_post(self):
        Window.release_all_keyboards()
        label = self.ids.verified
        if label.text == 'unverified':
            self.ids._screen_manager.current = 'login'
            return
        self.ids._screen_manager.current = 'loading'
        self.ids.loading.anim_load()
        self.post = self.ids.post.text
        print('submit: %s' % self.post)
        Clock.schedule_once(partial(self.login_m,self.post),1)


    def post_adjust_height(self,post,width):
        
        ratio = dp(6.9)
        a=float(post)
        b=float(width)
        c=a*ratio/b
        if (a*ratio/b)%1 > 0: 
            c+=1
        height = int(c)*dp(20)
        return height


    def post_back(self):
        Window.release_all_keyboards()
        self.ids._screen_manager.current = 'msgs'


    def get_data_app(self, doc2):

        self.req_app, posts,links,order,times = [], [], [], [], []
        i,j = 0, 0
        testlinks=True
        try:
            doc2.cssselect('#outputList > li > a')[0].get('href')
        except IndexError:
            testlinks=False
            print 'No Links'

        for entry in doc2.cssselect('#outputList'):
            for x in range(0, 50, 1):
                if testlinks:
                    if doc2.cssselect('#outputList > li > a')[0].text_content() in \
                            entry.cssselect('#outputList > li')[x].text_content():
                        link=entry.cssselect('#outputList > li > a')[i].get('href')
                        links+=[link]
                        i+=1
                    else:
                        link = 'na'
                        links +=[link]
                else:
                    link = 'na'
                    links +=[link]
                post = entry.cssselect('#outputList > li')[x].text_content()
                posts += [post]
                time = entry.cssselect('#outputList > li > span')[x].get('title')
                times+=[time]
                j+=1
                order+=[j]
                data={ 'entry': x+1, 'msg': post, 'url': link, 'time': time}
                self.req_app += [data]


        print('number of posts via app: %i' % len(self.req_app))
        self.req2 = self.translate_unicode(self.req_app)
        self.seperate_name(self.req2)
        self.add_hyperlinks(self.req2)
        self.build_board()


    def data_callback(self, requ, result):
        self.req = result

        print('number of posts: %i' % len(self.req))
        self.req2 = self.translate_unicode(self.req)
        self.seperate_name(self.req2)
        self.add_hyperlinks(self.req2)
        self.build_board()


    def start(self):

        self.ids.loading.anim_load()
        print('start fired')
        self.load_notes()
       
        if self.data2['user'] == '':
            self.get_data()
        else:
            Clock.schedule_once(self.login_m,1)


    def refresh(self):
        self.ids.loading.anim_load()
        self.ids._screen_manager.current = 'loading'

        if self.data2['user'] == '':
            Clock.schedule_once(self.get_data,1)
        else:
            Clock.schedule_once(self.login_m,1)


    def get_data(self, *args):

        self.requ = UrlRequest('https://free-ec2.scraperwiki.com/fmu2kwa/b4f746c592224f3/sql/?q=select%20%0A%09msg%2C%'
                              '0A%09entry%2C%0A%09url%2C%0A%20%20%20%20time%0Afrom%20swdata%0A--%20where%20url%20%3E%'
                              '20%0Aorder%20by%20entry%0Alimit%2050', on_success=self.data_callback,
                               on_error=self._on_error)


    def translate_unicode(self, data_got):

        data = [{'msg':'','name':'','time':'','url':'','len':0} for _ in range(0, 50, 1)]
        
        for x in range(0, len(data_got), 1):
            data[x]['msg'] += data_got[x]['msg']
            data[x]['time'] += data_got[x]['time'].encode('ascii', 'replace')+' ago'
            data[x]['url'] += data_got[x]['url'].encode('ascii', 'replace')
        
        return data


    def seperate_name(self,data):

        for x in range(0, len(data), 1):

            y = data[x]['msg']
            i=0
            for char in y:
                if char == ':':
                    
                    data[x]['name']='[color=#7F0000][b]'+(y[:i+1])+'[/b][/color]'
                    data[x]['msg']=(y[i+1:])
                    data[x]['len'] += len(data[x]['msg'])
                    break
                i+=1
        

    def add_hyperlinks(self, data):

        for x in range(0, len(data), 1):
            y = data[x]['msg']  

            if ('\u00ABlink\u00BB').decode('unicode_escape') in y:
                
                z = '[color=#7F0000][b][ref=' + data[x]['url'] + ']<<LINK>>[/ref][/b][/color]'
                data[x]['msg'] = y.replace(('\u00ABlink\u00BB').decode('unicode_escape'), z)


    def build_board(self):

        self.ids.screen_msgs_scroll.clear_widgets()

        board = PostyBase()
        post_len = []

        for x in range(0, 50, 1):
            post_len += [self.req2[x]['len']]
            y = self.post_adjust_height(self.req2[x]['len'], self.ids.first_box.width)

            header = HeaderPost()

            if x%2 == 0:
                header.r = 0.9686
                header.g = 0.9529
                header.b = 0.8275
            else:
                header.r = 0.9843
                header.g = 0.9765
                header.b = 0.9137

            header.ids.header_name.text = self.req2[x]['name']
            header.ids.header_time.text = self.req2[x]['time']

            board.add_widget(header)

            if x%2 == 0:
                board.add_widget(Posty(text=self.req2[x]['msg'], height=y))
            else:
                board.add_widget(Posty2(text=self.req2[x]['msg'], height=y))

        self.ids.screen_msgs_scroll.add_widget(board)
        self.ids._screen_manager.current = 'msgs'
        self.ids.loading.anim_close()


class PostyBase(StackLayout):
    pass


class Posty(Label):

    def openurl(self, *args):
        print "openurl fired"
        webbrowser.open(args[1])


class Posty2(Label):

    def openurl2(self, *args):
        print "openurl2 fired"
        webbrowser.open(args[1])


class HeaderPost(BoxLayout):

    r,g,b = NumericProperty(0),NumericProperty(0),NumericProperty(0)

    def __init__(self,**kwargs):
        super(HeaderPost, self).__init__(**kwargs)


class CustomButton(Button):
    pass


class Loading(StackLayout):
    curimg = 1

    def __init__(self, **kwargs):
        super(Loading, self).__init__(**kwargs)
        self.anim = True


    def nxt(self, dt):
        while self.anim:

            self.ids.img.source = 'atlas://data/loading_m.atlas/{}'.format(self.curimg)
            self.curimg += 1
            if self.curimg >= 13:
                self.curimg = 1
            sleep(dt)


    def anim_load(self, *args):
        self.anim = True
        thread = Thread(target=self.nxt, args=(float(1)/15,))
        thread.start()


    def anim_close(self):
        self.anim = False


class MomitApp(App):

    def build(self):

        self.root = RootWindow()
        self.root.save_path = self.user_data_dir
        Clock.schedule_once(self.start,0)

        return self.root


    def start(self, *args):
        self.root.start()


if __name__ == '__main__':
    MomitApp().run()
