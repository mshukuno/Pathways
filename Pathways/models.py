from Pathways.server import db
from citext import CIText


class Aphis(db.Model):
    __tablename__ = 'F280'
    F280_ID = db.Column(db.Integer, primary_key=True)
    REPORT_DT = db.Column(db.DateTime)
    PATHWAY= db.Column(db.String(20))
    FY = db.Column(db.Integer)
    MON = db.Column(db.Integer)
    LOCATION = db.Column(db.String(126))
    COMMODITY = db.Column(db.String(150))
    CTYPE_CD = db.Column(db.String(2))
    CTYPE_NM = db.Column(db.String(25))
    CFORM_NM = db.Column(db.String(20))
    DISP_CD = db.Column(db.String(4))
    DISP_NM = db.Column(db.String(255))    
    ORIGIN_NM = db.Column(db.String(50))
    DEST_NM = db.Column(db.String(20))
    QUANTITY = db.Column(db.Integer)
    NUM_SHIP = db.Column(db.Integer)    
    ENTRY_NUM = db.Column(db.String(50))
    CONTAINER_NUM = db.Column(db.String(50))
    BILL_NUM = db.Column(db.String(50))
    HOUSE_BILL_NUM = db.Column(db.String(50))
    EAN_ID = db.Column(db.String(50))
    city_fid = db.Column(db.Integer, db.ForeignKey('city.city_fid'))
    country_fid = db.Column(db.Integer, db.ForeignKey('country.country_fid'))
    disp_fid = db.Column(db.Integer, db.ForeignKey('disp_code.disp_fid'))

    

    def __init__(self, F280_ID, REPORT_DT, PATHWAY, FY, MON, LOCATION, COMMODITY, 
        CTYPE_CD, CTYPE_NM, CFORM_NM, DISP_CD, DISP_NM, ORIGIN_NM, DEST_NM, QUANTITY, NUM_SHIP,
        ENTRY_NUM, CONTAINER_NUM, BILL_NUM, HOUSE_BILL_NUM, EAN_ID, city_fid, country_fid, disp_fid):
        self.F280_ID = F280_ID
        self.REPORT_DT = REPORT_DT
        self.PATHWAY = PATHWAY
        self.FY = FY
        self.MON = MON
        self.LOCATION = LOCATION
        self.COMMODITY = COMMODITY
        self.CTYPE_CD = CTYPE_CD
        self.CTYPE_NM = CTYPE_NM
        self.CFORM_NM = CFORM_NM
        self.DISP_CD = DISP_CD
        self.DISP_NM = DISP_NM 
        self.ORIGIN_NM = ORIGIN_NM
        self.DEST_NM = DEST_NM  
        self.QUANTITY = QUANTITY
        self.NUM_SHIP = NUM_SHIP     
        self.ENTRY_NUM = ENTRY_NUM
        self.CONTAINER_NUM = CONTAINER_NUM
        self.BILL_NUM = BILL_NUM
        self.HOUSE_BILL_NUM = HOUSE_BILL_NUM
        self.EAN_ID = EAN_ID
        self.city_fid = city_fid
        self.country_fid = country_fid
        self.disp_fid = disp_fid



    # def __repr__(self):
    #     return 'Aphis<{0}, {1}, {2}, {3}, {4}, {5}>'.format(
    #         self.F280_ID, self.REPORT_DT, self.FY, self.MON, self.PATHWAY, 
    #         self.ORIGIN_NM, self.LOCATION, self.COMMODITY, self.CFORM_NM, self.DISP_CD, 
    #         self.DISP_NM, self.QUANTITY, self.NUM_SHIP)


class Disp(db.Model):
    __tablename__ = 'disp_code'
    disp_code = db.Column(db.String(4))   
    disp_desc = db.Column(db.String(255))
    disp_group = db.Column(db.String(5))    
    disp_fid = db.Column(db.Integer, primary_key=True)
    pest_found = db.Column(db.String(10)) 

    disprel = db.relationship('Aphis')

    def init(self, disp_code, disp_desc, disp_group, disp_fid, pest_found):
        self.disp_code = disp_code
        self.disp_desc = disp_desc
        self.disp_group = disp_group
        self.disp_fid = disp_fid
        self.pest_found = pest_found


class City(db.Model):
    __tablename__ = 'city'
    city_fid = db.Column(db.Integer, primary_key=True)
    state_abbrv = db.Column(db.String(2))
    city = db.Column(db.String(180))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def init(self, city_fid, state_abbrv, city, latitude, longitude):
        self.city_fid = city_fid
        self.state_abbrv = state_abbrv
        self.city = city
        self.latitude = latitude
        self.longitude = longitude


class Country(db.Model):
    __tablename__ = 'country'
    country_fid = db.Column(db.Integer, primary_key=True)
    fip = db.Column(db.String(2))
    iso2 = db.Column(db.String(3))
    iso3 = db.Column(db.String(3))
    un = db.Column(db.String(5))
    name = db.Column(db.String(255))
    region = db.Column(db.String(3))
    subregion = db.Column(db.String(3))
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    region_name = db.Column(db.String(255))
    subregion_name = db.Column(db.String(255))

    def init(self, country_fid, fip, iso2, iso3, un, name, region, 
        subregion, longitude, latitude, region_name, subregion_name):
        self.country_fid = country_fid
        self.fip = fip
        self.iso2 = iso2
        self.iso3 = iso3
        self.un = un
        self.name = name
        self.region = region
        self.subegion = subregion
        self.longitude = longitude
        self.latitude = latitude
        self.region_name = region_name
        self.subregion_name = subregion_name



