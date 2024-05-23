from datetime import date,timedelta

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

    def orgnize(self,isOpenOrgnize:bool,ffrom:str,to:str,bookId:str,personId:str='')->str:
        """
        整理时调用
        返回错误信息，否则返回空字符串
        """
        if ffrom=='bro' and to=='bs':
            if self.bro[bookId]<=0:
                return '借还处查无此书'
            else:
                self.bro[bookId]-=1
                self.bs[bookId]+=1
        elif ffrom=='ao' and to=='bs':
            for i in range(0,self.ao.__len__()):
                if self.ao[i][2]==bookId and self.ao[i][3] ==False:
                    self.ao.pop(i)
                    self.bs[bookId]+=1
                    return ''
            return '预约处查无此书或尚在留存中'
        elif ffrom=='bs' and to=='ao':
            if self.bs[bookId]<=0:
                return '书架查无此书'
            for i in range(0,self.aoLog.__len__()):
                if self.aoLog[i][0]==personId and self.aoLog[i][1]==bookId:
                    self.aoLog.pop(i)
                    self.bs[bookId]-=1
                    if isOpenOrgnize:
                        self.ao.append((self.datetime,personId,bookId,True))
                    else:
                        self.ao.append((self.datetime+timedelta(days=1), personId, bookId, True))
                    return ''
            return '没有此人的预约记录'
        elif ffrom=='bro' and to=='ao':
            if self.bro[bookId]<=0:
                return '借还处查无此书'
            for i in range(0,self.aoLog.__len__()):
                if self.aoLog[i][0]==personId and self.aoLog[i][1]==bookId:
                    self.aoLog.pop(i)
                    self.bro[bookId]-=1
                    if isOpenOrgnize:
                        self.ao.append((self.datetime, personId, bookId, True))
                    else:
                        self.ao.append((self.datetime + timedelta(days=1), personId, bookId, True))
                    return ''
            return '没有此人的预约记录'
        elif ffrom=='bs' and to=='bro':
            if self.bs[bookId]<=0:
                return '借还处查无此书'
            else:
                self.bs[bookId]-=1
                self.bro[bookId]+=1
        elif ffrom=='ao' and to=='bro':
            for i in range(0, self.ao.__len__()):
                if self.ao[i][2] == bookId and self.ao[i][3] == False:
                    self.ao.pop(i)
                    self.bro[bookId] += 1
                    return ''
            return '预约处查无此书或尚在留存中'
        else:
            return '起点和终点重复'
        return ''

library=Library()
