from datetime import date,timedelta
import re

class Person:
    def __init__(self,id):
        self.id=id
        self.books=set()
        self.typeB=False
    def add_book(self,bookId):
        if 'B' in bookId:
            self.typeB=True
        self.books.add(bookId)
    def del_book(self,bookId):
        if 'B' in bookId:
            self.typeB=False
        self.books.remove(bookId)
    def has_book(self,bookId)->bool:
        return bookId in self.books
    def has_B_book(self)->bool:
        return self.typeB

    def get_books(self)->set:
        return self.books




class Library:
    def __init__(self):
        self.bs={}  #书架,{bookId:str,count:int}
        self.bro={} #借还处,{bookId:str,count:int}
        self.ao=[]  #预约处,[(datetime:date,personId:str,bookId:str,ordered:bool)]
        self.aoLog=[]   #预约记录,[(personId:str,bookId:str)]
        self.datetime=date(2024,1,1)
        self.persons={} #人,{personId:str,person:Person}
    def add_book(self,book:str,count:int=1):
        self.bs[book]=count
        self.bro[book]=0
    def update(self,datetime:date):
        """
        每次开馆时更新当前时间
        同时更新预约处的书
        """
        self.datetime=datetime
        for i in range(0,self.ao.__len__()):
            if (self.datetime-self.ao[i][0]).days>=5:
                self.ao[i]=(self.ao[i][0],self.ao[i][1],self.ao[i][2],False)
    def open_check(self)->str:
        """
        开馆整理后调用
        检查借还处不应该有书，预约处不应该有逾期的书
        """
        for i in self.bro.keys():
            if self.bro[i]!=0:
                return '借还处不应有书'+i
        for i in range(0, self.ao.__len__()):
            if (self.datetime - self.ao[i][0]).days >= 5:
                return '预约处不应有逾期的书'+str(self.ao[i])
        return ''

    def borrow(self,personId:str,bookId:str)->str:
        """
        返回'accept'或'reject'
        """
        if personId not in self.persons:
            self.persons[personId]=Person(personId)
        if bookId not in self.bs or self.bs[bookId]==0 or 'A' in bookId:
            return 'reject'
        elif self.persons[personId].has_book(bookId) or ('B' in bookId and self.persons[personId].has_B_book()):
            self.bs[bookId]-=1
            self.bro[bookId]+=1
            return 'reject'
        else:
            self.bs[bookId]-=1
            self.persons[personId].add_book(bookId)
            return 'accept'
    def return_book(self,personId:str,bookId:str)->str:
        """
        返回'accept'或错误信息
        """
        if personId not in self.persons:
            return '查无此人'
        elif bookId not in self.persons[personId].books:
            return '此人无此书'
        self.bro[bookId]+=1
        self.persons[personId].del_book(bookId)
        return 'accept'
    def order(self,personId:str,bookId:str)->str:
        """
        返回'accept'或'reject'
        """
        if personId not in self.persons:
            self.persons[personId]=Person(personId)
        if 'A' in bookId or ('B' in bookId and self.persons[personId].has_B_book()) or self.persons[personId].has_book(bookId):
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
                self.persons[personId].add_book(bookId)
                return 'accept'
        return 'reject'
    def query(self,bookId:str)->int:
        """
        返回数量
        """
        return self.bs[bookId]

    def action(self,input:str,output:str)->str:
        tmp_match=re.match('\[(\d{4})-(\d{2})-(\d{2})\].*', input)
        time1 = date(int(tmp_match.group(1)), int(tmp_match.group(2)), int(tmp_match.group(3)))
        tmp_match = re.match('\[(\d{4})-(\d{2})-(\d{2})\].*', output)
        time2 = date(int(tmp_match.group(1)), int(tmp_match.group(2)), int(tmp_match.group(3)))
        if time1!=time2:
            return '时间错误'
        tmp_match=re.match('\[(\d{4})-(\d{2})-(\d{2})\] (\w+) (\w+) ([ABC]-\d{4})', input)
        personId = tmp_match.group(4)
        bookId = tmp_match.group(6)
        command = tmp_match.group(5)
        if 'queried' in input:
            tmp_match = re.match('\[\d{4}-\d{2}-\d{2}\] ([ABC]-\d{4}) (\d+)', output)
            if bookId!=tmp_match.group(1):
                return '查询书籍id错误'
            elif self.query(bookId)!=int(tmp_match.group(2)):
                return '查询书籍数量错误'
        else:
            tmp_match = re.match('\[\d{4}-\d{2}-\d{2}\] \[(\w+)\] (\w+) (\w+) ([ABC]-\d{4})', output)
            if personId!=tmp_match.group(2):
                return '查询学号错误'
            elif bookId!=tmp_match.group(4):
                return '查询书籍错误'
            if tmp_match.group(3)=='borrowed':
                if self.borrow(personId,bookId)!=tmp_match.group(1):
                    return 'accept或reject不匹配'
            if tmp_match.group(3)=='ordered':
                if self.order(personId,bookId)!=tmp_match.group(1):
                    return 'accept或reject不匹配'
            if tmp_match.group(3)=='returned':
                if self.return_book(personId,bookId)!=tmp_match.group(1):
                    return 'accept或reject不匹配'
            if tmp_match.group(3)=='picked':
                if self.pick(personId,bookId)!=tmp_match.group(1):
                    return 'accept或reject不匹配'
        return ''

    def orgnize(self,isOpenOrgnize:bool,command:str)->str:
        """
        整理时调用
        返回错误信息，否则返回空字符串
        """
        ffrom='';to='';bookId='';personId=''
        try:
            if 'for' in command:
                tmp_match = re.match('\[\d{4}-\d{2}-\d{2}\] move ([ABC]-\d{4}) from (\w+) to (\w+) for (\w+)',command)
                bookId=tmp_match.group(1)
                ffrom=tmp_match.group(2)
                to=tmp_match.group(3)
                personId=tmp_match.group(4)
            else:
                tmp_match = re.match('\[\d{4}-\d{2}-\d{2}\] move ([ABC]-\d{4}) from (\w+) to (\w+)', command)
                bookId = tmp_match.group(1)
                ffrom = tmp_match.group(2)
                to = tmp_match.group(3)
        except:
            return '格式错误'
        if ffrom=='bro' and to=='bs':
            if self.bro[bookId]<=0:
                return '借还处查无此书'+bookId
            else:
                self.bro[bookId]-=1
                self.bs[bookId]+=1
        elif ffrom=='ao' and to=='bs':
            for i in range(0,self.ao.__len__()):
                if self.ao[i][2]==bookId and self.ao[i][3] ==False:
                    self.ao.pop(i)
                    self.bs[bookId]+=1
                    return ''
            return '预约处查无此书或尚在留存中'+bookId
        elif ffrom=='bs' and to=='ao':
            if self.bs[bookId]<=0:
                return '书架查无此书'+bookId
            for i in range(0,self.aoLog.__len__()):
                if self.aoLog[i][0]==personId and self.aoLog[i][1]==bookId:
                    self.aoLog.pop(i)
                    self.bs[bookId]-=1
                    if isOpenOrgnize:
                        self.ao.append((self.datetime,personId,bookId,True))
                    else:
                        self.ao.append((self.datetime+timedelta(days=1), personId, bookId, True))
                    return ''
            return '没有此人的预约记录'+personId
        elif ffrom=='bro' and to=='ao':
            if self.bro[bookId]<=0:
                return '借还处查无此书'+bookId
            for i in range(0,self.aoLog.__len__()):
                if self.aoLog[i][0]==personId and self.aoLog[i][1]==bookId:
                    self.aoLog.pop(i)
                    self.bro[bookId]-=1
                    if isOpenOrgnize:
                        self.ao.append((self.datetime, personId, bookId, True))
                    else:
                        self.ao.append((self.datetime + timedelta(days=1), personId, bookId, True))
                    return ''
            return '没有此人的预约记录'+personId
        elif ffrom=='bs' and to=='bro':
            if self.bs[bookId]<=0:
                return '借还处查无此书'+bookId
            else:
                self.bs[bookId]-=1
                self.bro[bookId]+=1
        elif ffrom=='ao' and to=='bro':
            for i in range(0, self.ao.__len__()):
                if self.ao[i][2] == bookId and self.ao[i][3] == False:
                    self.ao.pop(i)
                    self.bro[bookId] += 1
                    return ''
            return '预约处查无此书或尚在留存中'+bookId
        else:
            return '起点和终点重复'
        return ''

library=Library()
