from ..extentions import db


class RoleModel(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    description = db.Column(db.String(255), nullable=True)

    users = db.relationship("UserModel", backref="role", lazy="subquery")
