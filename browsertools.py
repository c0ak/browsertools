from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from PIL import Image
import random, time, string, os

def wait(min=1, max=3):
    if min > max:
        max = min + 1
    time.sleep(round(random.uniform(min, max), 2))
    
def generateData(length=10, digits=True, letters=True, characters=False, upper=True, lower=True):
    source = ""
    if digits == True:
        source += string.digits
    if letters == True:
        if upper == True:
            source += string.ascii_uppercase
        if lower == True:
            source += string.ascii_lowercase
    if characters == True:
        source += """!@#$%^&*()_+-="'[],./;':"""
    output = ""
    for i in range(length):
        output += random.choice(source)
    return output
        

class Browser:
    def __init__(self):
        self.profile = webdriver.FirefoxProfile()
        self.driver = None
        self.prefs = {}
        self.captchaAPI = {"text": "", "recaptcha": ""}
        self.auth = ""
        self.size = ""
        
    def startDriver(self, browser='Firefox', profile=None):
        browser = browser.lower()
        if browser == 'firefox':
            if profile == None:
                profile = self.profile
            self.driver = webdriver.Firefox(profile)
        if self.auth:
            self.setProxyAuth(self.auth)
        if self.size:
            self.driver.set_window_size(size[0], size[1])
        self.driver.implicitly_wait(10)
        return self.driver
    
    def setPref(self, target, value):
        if self.driver == None and self.profile != None:
            self.profile.set_preference(target, value)
        elif self.driver != None:
            ac = ActionChains(self.driver)
            ac.key_down(Keys.SHIFT).send_keys(Keys.F2).key_up(Keys.SHIFT).perform()
            ac.send_keys('pref set {} {}'.format(target, str(value))).perform()
            ac.send_keys(Keys.ENTER).perform()
            ac.key_down(Keys.SHIFT).send_keys(Keys.F2).key_up(Keys.SHIFT).perform()
            ac.key_down(Keys.SHIFT).send_keys(Keys.F2).key_up(Keys.SHIFT).perform()
        else:
            return False
        self.prefs[str(target)] = value
    
    def setProxy(self, proxy, auth="", types=["http", "https", "ftp", "socks", "ssl"]):
        if "@" in proxy:
            auth, proxy = proxy.split('@')
        self.proxy, self.proxyp = proxy.split(':')
        self.setPref("network.proxy.type", 1)
        self.auth = auth
        for eachType in types:
            proxystring = 'network.proxy.' + eachType
            self.setPref(proxystring, self.proxy)
            self.setPref(proxystring + '_port', int(self.proxyp))
        if self.driver and auth:
            self.setProxyAuth(auth)
            
    def setProxyAuth(self, auth):
        auth = self.auth.split(":")
        time.sleep(1)
        while True:
            try:
                alert = self.driver.switch_to_alert()
                alert.send_keys(auth[0])
                break
            except:
                time.sleep(0.5)
        alert.send_keys(Keys.TAB + auth[1])
        alert.accept() 
        self.auth = auth
    
    def getScrollPosition(self, axis='y'):
        return self.driver.execute_script("return window.page{}Offset;".format(axis.upper()))
    
    def getSiteKey(self):
        try:
            sitekey = self.driver.find_element_by_class_name("g-recaptcha").get_attribute('data-sitekey')
        except:
            sitekey = self.driver.find_element_by_class_name("NoCaptcha").get_attribute('data-sitekey')
        return sitekey
        
    def setUseragent(self, value):
        self.setPref('general.useragent.override', value)
        self.useragent = value

    def randomType(self, target, value, min=0.1, max=1.1):
        for eachChar in value:
            target.send_keys(eachChar)
            wait(min, max)
            
    def setWindowSize(self, sizes=["1920x1080", "1366x768", "1280x1024", "1280x800", "1024x768"], handle='current'):
        t = random.choice(sizes).split('x')
        if self.driver == None:
            self.size = t
        else:
            self.driver.set_window_size(t[0], t[1], handle)
              
    def get(self, url):
        finished = 0
        i = 0
        while finished == 0:
            if i > 5:
                return False
            try:
                self.driver.get(url)
                finished = 1
            except:
                wait()
                i += 1
        return True
    
    def savePic(self, elem, output):
        location = elem.location
        size = elem.size
        offset = self.getScrollPosition()
        location['y'] += offset
        self.driver.save_screenshot(output)
        image = Image.open(output)
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        image = image.crop((left, top, right, bottom))
        image.save(output, 'png')        
        
    def select(self, elem, by, value):
        t = Select(elem)
        if by == 'value':
            t.select_by_value(value)
        elif by == 'index':
            t.select_by_index(value)
    
    def scrollTo(self, elem='', y='', x=''):
        if elem:
            self.driver.execute_script("return arguments[0].scrollIntoView();", elem)
            self.driver.execute_script("window.scrollBy(0, -150);")
        if y:
            self.driver.execute_script("window.scrollTo(" + str(y) + ", Y)")
        if x:
            self.driver.execute_script("window.scrollTo(" + str(x) + ", X)")
    
    def hide(self):
        self.driver.set_window_position(-3000, 0)
        self.hidden = True
    
    def unhide(self):
        self.driver.set_window_position(0, 0)
        self.hidden = False
        
    def inject(self, target, value, elemtype='id'):
        elemtype = elemtype.lower()
        getelemstring = "getElementBy{}"
        if elemtype == 'id':
            getelemstring.format('Id')
        self.driver.execute_script('document.' + getelemstring + '(' + target + ').value = "' + value + '"')

if __name__ == "__main__":
    b = Browser()
    b.startDriver()
