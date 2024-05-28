from datetime import date,timedelta
import re
import json

class Person:
    def __init__(self,id):
        self.id=id
        self.books={}
        self.typeB=False
        self.typeBU=False
    def add_book(self,bookId:str,deadline:date):
        if 'BU' in bookId:
            self.typeBU=True
        elif 'B' in bookId:
            self.typeB=True
        self.books[bookId]=deadline
    def del_book(self,bookId):
        if 'BU' in bookId:
            self.typeBU=False
        elif 'B' in bookId:
            self.typeB=False
        self.books.pop(bookId)
    def has_book(self,bookId)->bool:
        return bookId in self.books
    def has_B_book(self)->bool:
        return self.typeB
    def has_BU_book(self)->bool:
        return self.typeBU
    def get_books(self)->dict:
        return self.books
    def get_time(self,bookId:str)->date:
        return self.books[bookId]
    def change_time(self,bookId:str,deadline:date):
        self.books[bookId]=deadline



class Library:
    def __init__(self):
        self.bs={}  #书架,{bookId:str,count:int}
        self.bro={} #借还处,{bookId:str,count:int}，有key则一定不为0
        self.bdc={} #漂流角,{bookId:str,count:int}，成为正式图书后会被移除
        self.bdcHot={}  #漂流角的图书借阅次数,{bookId:str,count:int}，成为正式图书后会被移除
        self.ao=[]  #预约处,[(today:date,personId:str,bookId:str,ordered:bool)]
        self.aoLog=[]   #预约记录,[(personId:str,bookId:str)]
        self.today=date(2024, 1, 1)
        self.persons={} #人,{personId:str,person:Person}
    def add_book(self,book:str,count:int=1):
        self.bs[book]=count
    def update(self,isclose:bool,today:date):
        """
        每次开馆时更新当前时间
        闭馆时更新预约处的书
        """
        if isclose:
            for i in range(0,self.ao.__len__()):
                if (self.today - self.ao[i][0]).days>=4:
                    self.ao[i]=(self.ao[i][0],self.ao[i][1],self.ao[i][2],False)
        else:
            self.today=today
            for i in range(0,self.ao.__len__()):
                if (self.today - self.ao[i][0]).days>=5:
                    self.ao[i]=(self.ao[i][0],self.ao[i][1],self.ao[i][2],False)
    def open_check(self)->str:
        """
        开馆整理后调用
        检查借还处不应该有书，预约处不应该有逾期的书
        漂流角达到2次的书应该被移动走
        """
        if self.bro.__len__()!=0:
            return '开馆整理后借还处不应有书'+self.bro.keys().__str__()
        for i in self.bdc.keys():
            if self.bdcHot[i]>=2:
                return '开馆整理后漂流角不应有借阅次数大于等于2的书'+i
        for i in range(0, self.ao.__len__()):
            if (self.today - self.ao[i][0]).days >= 5:
                return '开馆整理后预约处不应有逾期的书'+str(self.ao[i])
        return ''

    def borrow(self,personId:str,bookId:str)->str:
        """
        返回'accept'或'reject'
        """
        if personId not in self.persons:
            self.persons[personId]=Person(personId)
        person=self.persons[personId]
        if 'U' in bookId:
            if bookId not in self.bdc or self.bdc[bookId]==0 or 'A' in bookId:
                return 'reject'
            elif person.has_book(bookId) or ('B' in bookId and self.persons[personId].has_BU_book()):
                self.bdc[bookId] -= 1
                if bookId not in self.bro:
                    self.bro[bookId]=1
                else:
                    self.bro[bookId]+=1
                return 'reject'
            else:
                self.bdc[bookId]-=1
                if 'B' in bookId:
                    person.add_book(bookId, self.today+timedelta(days=7))
                else:
                    person.add_book(bookId,self.today+timedelta(days=14))
                return 'accept'
        else:
            if bookId not in self.bs or self.bs[bookId]==0 or 'A' in bookId:
                return 'reject'
            elif self.persons[personId].has_book(bookId) or ('B' in bookId and self.persons[personId].has_B_book()):
                self.bs[bookId]-=1
                if bookId not in self.bro:
                    self.bro[bookId] = 1
                else:
                    self.bro[bookId] += 1
                return 'reject'
            else:
                self.bs[bookId]-=1
                if 'B' in bookId:
                    self.persons[personId].add_book(bookId,self.today+timedelta(days=30))
                else:
                    self.persons[personId].add_book(bookId, self.today + timedelta(days=60))
                return 'accept'
    def return_book(self,personId:str,bookId:str)->(str,bool):
        """
        返回'accept'或错误信息
        返回是否逾期
        """
        if personId not in self.persons:
            return '查无此人',False
        elif bookId not in self.persons[personId].books:
            return '数据生成有误，请忽略此条数据',False
        person=self.persons[personId]
        due=person.get_time(bookId)<self.today
        if bookId not in self.bro:
            self.bro[bookId] = 1
        else:
            self.bro[bookId] += 1
        person.del_book(bookId)
        if bookId in self.bdcHot:
            self.bdcHot[bookId]+=1
        return 'accept',due
    def order(self,personId:str,bookId:str)->str:
        """
        返回'accept'或'reject'
        """
        if personId not in self.persons:
            self.persons[personId]=Person(personId)
        person=self.persons[personId]
        if 'U' in bookId:
            return 'reject'
        if 'A' in bookId or ('B' in bookId and person.has_B_book()) or person.has_book(bookId):
            return 'reject'
        else:
            self.aoLog.append((personId,bookId))
            return 'accept'
    def pick(self,personId:str,bookId:str)->str:
        """
        返回'accept'或'reject'
        """
        if personId not in self.persons:
            self.persons[personId]=Person(personId)
        if 'A' in bookId or ('B' in bookId and self.persons[personId].has_B_book()) or self.persons[personId].has_book(bookId):
            return 'reject'
        for i in range(0,self.ao.__len__()):
            if self.ao[i][1] == personId and self.ao[i][2] == bookId and self.ao[i][3] ==True:
                self.ao.pop(i)
                if 'B' in bookId:
                    self.persons[personId].add_book(bookId,self.today+timedelta(days=30))
                else:
                    self.persons[personId].add_book(bookId, self.today + timedelta(days=60))
                return 'accept'
        return 'reject'
    def query(self,bookId:str)->int:
        """
        返回数量
        """
        if 'U' in bookId:
            return self.bdc[bookId]
        else:
            return self.bs[bookId]
    def renew(self,personId:str,bookId:str)->str:
        if personId not in self.persons:
            self.persons[personId]=Person(personId)
        person=self.persons[personId]
        if not person.has_book(bookId):
            return '该同学没有这本书'+bookId
        days=(person.get_time(bookId)-self.today).days
        if days<0 or days>=5:
            return 'reject'
        if 'U' in bookId:
            return 'reject'
        if self.bs[bookId]==0:
            for i in self.ao:
                if i[2]==bookId:
                    return 'reject'
            for i in self.aoLog:
                if i[1]==bookId:
                    return 'reject'
        person.change_time(bookId,person.get_time(bookId)+timedelta(days=30))
        return 'accept'
    def donate(self,bookId:str)->str:
        self.bdc[bookId]=1
        self.bdcHot[bookId]=0
        return 'accept'

    def action(self,input:str,output:str)->str:
        tmp_match=re.match(r'\[(\d{4})-(\d{2})-(\d{2})\].*', input)
        time1 = date(int(tmp_match.group(1)), int(tmp_match.group(2)), int(tmp_match.group(3)))
        tmp_match = re.match(r'\[(\d{4})-(\d{2})-(\d{2})\].*', output)
        time2 = date(int(tmp_match.group(1)), int(tmp_match.group(2)), int(tmp_match.group(3)))
        if time1!=time2:
            return '时间错误'
        tmp_match=re.match(r'\[(\d{4})-(\d{2})-(\d{2})\] (\w+) (\w+) ([ABCU]{1,2}-\d{4})', input)
        personId = tmp_match.group(4)
        bookId = tmp_match.group(6)
        command = tmp_match.group(5)
        if 'queried' in input:
            tmp_match = re.match(r'\[\d{4}-\d{2}-\d{2}\] ([ABCU]{1,2}-\d{4}) (\d+)', output)
            if bookId!=tmp_match.group(1):
                return '查询书籍id错误'
            elif self.query(bookId)!=int(tmp_match.group(2)):
                return '查询书籍数量错误'
        elif 'returned' in input:
            tmp_match = re.match(r'\[\d{4}-\d{2}-\d{2}\] \[(\w+)\] (\w+) (\w+) ([ABCU]{1,2}-\d{4}).*', output)
            if personId!=tmp_match.group(2):
                return '学号错误'
            elif bookId!=tmp_match.group(4):
                return '书籍id错误'
            result, due = self.return_book(personId, bookId)
            if result != tmp_match.group(1):
                return '应为 ' + result
            elif 'not' in output and due:
                return '书籍'+bookId+'已经逾期'
            elif 'not' not in output and not due:
                return '书籍'+bookId+'尚未逾期'
        else:
            tmp_match = re.match(r'\[\d{4}-\d{2}-\d{2}\] \[(\w+)\] (\w+) (\w+) ([ABCU]{1,2}-\d{4})', output)
            if personId!=tmp_match.group(2):
                return '学号错误'
            elif bookId!=tmp_match.group(4):
                return '书籍id错误'
            if tmp_match.group(3)=='borrowed':
                result=self.borrow(personId,bookId)
                if result!=tmp_match.group(1):
                    return '应为 '+result
            elif tmp_match.group(3)=='ordered':
                result=self.order(personId,bookId)
                if result!=tmp_match.group(1):
                    return '应为 '+result
            elif tmp_match.group(3)=='picked':
                result=self.pick(personId,bookId)
                if result!=tmp_match.group(1):
                    return '应为 '+result
            elif tmp_match.group(3)=='renewed':
                result=self.renew(personId,bookId)
                if result!=tmp_match.group(1):
                    return '应为 '+result
            elif tmp_match.group(3)=='donated':
                result=self.donate(bookId)
                if result!=tmp_match.group(1):
                    return '应为 '+result
            else:
                return '非法指令'
        return ''

    def orgnize(self,isOpenOrgnize:bool,command:str)->str:
        """
        整理时调用
        返回错误信息，否则返回空字符串
        """
        ffrom='';to='';bookId='';personId=''
        tmp_match = re.match(r'\[(\d{4})-(\d{2})-(\d{2})\].*', command)
        time1 = date(int(tmp_match.group(1)), int(tmp_match.group(2)), int(tmp_match.group(3)))
        if time1 != self.today:
            return '时间错误'
        try:
            if 'for' in command:
                tmp_match = re.match(r'\[\d{4}-\d{2}-\d{2}\] move ([ABCU]{1,2}-\d{4}) from (\w+) to (\w+) for (\w+)',command)
                bookId=tmp_match.group(1)
                ffrom=tmp_match.group(2)
                to=tmp_match.group(3)
                personId=tmp_match.group(4)
            else:
                tmp_match = re.match(r'\[\d{4}-\d{2}-\d{2}\] move ([ABCU]{1,2}-\d{4}) from (\w+) to (\w+)', command)
                bookId = tmp_match.group(1)
                ffrom = tmp_match.group(2)
                to = tmp_match.group(3)
        except:
            return '格式错误'
        if ffrom=='bro' and to=='bs':
            if bookId not in self.bro:
                return '借还处查无此书'+bookId
            elif 'U' in bookId and self.bdcHot[bookId]<2:
                return '书籍尚未被完整借阅2次'+bookId
            self.bro[bookId]-=1
            if self.bro[bookId]==0:
                self.bro.pop(bookId)
            if 'U' in bookId:
                self.bdc.pop(bookId)
                bookId = bookId.replace('U','')
            if bookId in self.bs:
                self.bs[bookId]+=1
            else:
                self.bs[bookId]=1
        elif ffrom=='ao' and to=='bs':
            for i in range(0,self.ao.__len__()):
                if self.ao[i][2]==bookId and self.ao[i][3] ==False:
                    self.ao.pop(i)
                    self.bs[bookId]+=1
                    return ''
            return '预约处查无此书或尚在留存中'+bookId
        elif ffrom=='bs' and to=='ao':
            if bookId not in self.bs or self.bs[bookId]<=0:
                return '书架查无此书'+bookId
            for i in range(0,self.aoLog.__len__()):
                if self.aoLog[i][0]==personId and self.aoLog[i][1]==bookId:
                    self.aoLog.pop(i)
                    self.bs[bookId]-=1
                    if isOpenOrgnize:
                        self.ao.append((self.today, personId, bookId, True))
                    else:
                        self.ao.append((self.today + timedelta(days=1), personId, bookId, True))
                    return ''
            return '没有此人的预约记录'+personId
        elif ffrom=='bro' and to=='ao':
            if bookId not in self.bro:
                return '借还处查无此书'+bookId
            for i in range(0,self.aoLog.__len__()):
                if self.aoLog[i][0]==personId and self.aoLog[i][1]==bookId:
                    self.aoLog.pop(i)
                    self.bro[bookId]-=1
                    if self.bro[bookId] == 0:
                        self.bro.pop(bookId)
                    if isOpenOrgnize:
                        self.ao.append((self.today, personId, bookId, True))
                    else:
                        self.ao.append((self.today + timedelta(days=1), personId, bookId, True))
                    return ''
            return '没有此人的预约记录'+personId
        elif ffrom=='bs' and to=='bro':
            if bookId not in self.bs or self.bs[bookId]<=0:
                return '书架查无此书'+bookId
            else:
                self.bs[bookId]-=1
                if bookId not in self.bro:
                    self.bro[bookId]=1
                else:
                    self.bro[bookId]+=1
        elif ffrom=='ao' and to=='bro':
            for i in range(0, self.ao.__len__()):
                if self.ao[i][2] == bookId and self.ao[i][3] == False:
                    self.ao.pop(i)
                    if bookId not in self.bro:
                        self.bro[bookId] = 1
                    else:
                        self.bro[bookId] += 1
                    return ''
            return '预约处查无此书或尚在留存中'+bookId
        elif ffrom=='bro' and to=='bdc':
            if bookId not in self.bro:
                return '借还处查无此书'+bookId
            elif 'U' not in bookId:
                return '此书不是漂流角书籍'+bookId
            else:
                self.bro[bookId]-=1
                self.bdc[bookId]+=1
            if self.bro[bookId]==0:
                self.bro.pop(bookId)
        else:
            return '起点和终点重复或移动不合法'
        return ''

def check():
    config=json.load(open('config.json',encoding='utf-8'))
    input_file=config['input_file']
    output_file=config['output_file']
    input=open(input_file,'r',encoding='utf-8').readlines()
    output=open(output_file,'r',encoding='utf-8').readlines()
    library=Library()

    i=1;j=0
    while i<=int(input[0]):
        tmp_match = re.match(r'([ABCU]{1,2}-\d{4}) (\d+).*', input[i])
        library.add_book(tmp_match.group(1),int(tmp_match.group(2)))
        i+=1
    while i<input.__len__() and j<output.__len__():
        input_command = input[i]
        i+=1
        output_command = []
        output_command.append(output[j])
        j+=1
        if not('-' in output_command[0] or int(output_command[0])==0):
            for k in range(0,int(output_command[0])):
                output_command.append(output[j+k])
            j+=int(output_command[0])
        if 'OPEN' in input_command:
            tmp_match = re.match(r'\[(\d{4})-(\d{2})-(\d{2})\].*', input_command)
            time = date(int(tmp_match.group(1)), int(tmp_match.group(2)), int(tmp_match.group(3)))
            library.update(False,time)
            if int(output_command[0])>0:
                for k in range(1,output_command.__len__()):
                    result=library.orgnize(True,output_command[k])
                    if result!='':
                        return result+' 输入第'+str(i)+'行 输出第'+str(j)+'行'
            result=library.open_check()
            if result!='':
                return result+' 输入第'+str(i)+'行 输出第'+str(j)+'行'
        elif 'CLOSE' in input_command:
            library.update(True, time)
            if int(output_command[0])>0:
                for k in range(1,output_command.__len__()):
                    result=library.orgnize(False,output_command[k])
                    if result!='':
                        return result+' 输入第'+str(i)+'行 输出第'+str(j)+'行'
        else:
            result=library.action(input_command,output_command[0])
            if result != '':
                return result+' 输入第'+str(i)+'行 输出第'+str(j)+'行'
    return "Accepted!"

if __name__ == '__main__':
    print(check())