'''
Created on Feb 12, 2016

@author: kumaran
'''
import psycopg2,sys
sys.path.append('/home/kumaran/git/bmrb/python/Metabolomics/StarParser/parser')
import bmrb,re
class BMRBDB(object):
    '''
    classdocs
    '''


    def __init__(self, dbname,user,host):
        '''
        Constructor
        '''
        self.conn=psycopg2.connect("dbname=%s user=%s host=%s"%(dbname,user,host))
    
    
   
        
    
    def find_ID(self,table,column_value,id):
        cmd="select \"%s\" from \"%s\" where "%(id,table)
        for cv in column_value[:-1]:
            cmd="%s \"%s\" = \'%s\' and "%(cmd,cv[0],cv[1])
        cmd="%s \"%s\" = \'%s\';"%(cmd,column_value[-1][0],column_value[-1][1])
        cur1=self.conn.cursor()
        cur1.execute(cmd)
        outdat=[i[0] for i in cur1.fetchall()]
        cur1.close()
        return outdat
        
    def insert_into(self,table,col_val,serial_id):
        cmd="insert into \"%s\" (\"%s\","%(table,serial_id)
        for i in col_val[:-1]:
            cmd="%s \"%s\","%(cmd,i[0])
        cmd="%s \"%s\") values (DEFAULT,"%(cmd,col_val[-1][0])
        for i in col_val[:-1]:
            cmd="%s \'%s\',"%(cmd,i[1])
        cmd="%s \'%s\');"%(cmd,col_val[-1][1])
        cur2=self.conn.cursor()
        cur2.execute(cmd)
        self.conn.commit()
        
        
    def getSTARTdata(self,bmrbid):
        self.starData=bmrb.entry.fromDatabase(bmrbid)
        for i in self.starData['entry_information'].tags:
            print i
    
    def close(self):
        self.conn.close()
        
    def get_dict(self,table):
        dat=open('../../StarToCuratedMapping.csv','r').read()
        dict=re.findall('%s,(\S+),(\S+),([\Ss]*)'%(table),dat)
        out_dict={}
        for i in dict:
            if i[1]!='serial':
                out_dict.update({i[1]:i[0]})
        return out_dict
    
    def load_table_Entry(self,bmrbid):
        dat=open('../../StarToCuratedMapping.csv','r').read()
        Entry_dict=self.get_dict('Entry')
        self.starData=bmrb.entry.fromDatabase(bmrbid)
        cv=[]
        for i in self.starData['entry_information'].tags:
            try:
                #print Entry_dict['_Entry.%s'%(i[0])],i[1]
                cv.append((Entry_dict['_Entry.%s'%(i[0])],i[1]))
            except KeyError:
                pass
        if len(self.find_ID('Entry', cv, 'DB_Entry_ID'))==0:
            self.insert_into('Entry', cv, 'DB_Entry_ID')
        else:
            print "Data for %s already exists"%(bmrbid)
            
            
    def load_table_Country(self):
        cur=self.conn.cursor()
        dat=open('../../country.txt','r').read().split("\n")[:-1]
        for country in dat:
            if len(self.find_ID('Country', [('Name', country)],'DB_Country_ID'))==0:
                cmd="insert into \"Country\" values(DEFAULT,\'%s\');"%(country)
                cur.execute(cmd)
                self.conn.commit()
            else:
                print country," already exists"
        cur.close()
        
        
    def list_table(self,table_name):
        self.cur1=self.conn.cursor()
        cmd="select * from \"%s\" ;"%(table_name)
        self.cur1.execute(cmd)
        for i in self.cur1.fetchall():
            print i
        self.cur1.close()
        
        








if __name__=="__main__":
    #p=BMRBDB('bmrb','web','manta.bmrb.wisc.edu')
    p=BMRBDB('bmrb','nmr','localhost')
    #p.load_table_Country()
    
    
    p.load_table_Entry('15060')
    p.close()
    #p.getSTARTdata(15060)