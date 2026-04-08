from .db import db
from datetime import datetime

class Dataset(db.Model):
    __tablename__ = "datasets"

    id            = db.Column(db.Integer,primary_key=True)
    filename      = db.Column(db.String(255) ,nullable=False)
    original      = db.Column(db.String(255))
    row_count     = db.Column(db.Integer)
    col_count     = db.Column(db.Integer)
    columns       = db.Column(db.Text)
    clean_report  = db.Column(db.Text)
    uploaded_at   = db.Column(db.DateTime,default=datetime.utcnow)


    def to_dict(self):
        return{
            "id":       self.id,
            "filename": self.filename,
            "original": self.original,
            "row_count":self.row_count,
            "col_count":self.col_count,
            "columns":  self.columns,
            "clean_report": self.clean_report,
            "uploaded_at":  str(self.uploaded_at),

        }
