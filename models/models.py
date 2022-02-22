import enum
import datetime
from datetime import timedelta, timezone

import sqlalchemy
from sqlalchemy import Column, Integer, String, Enum, ForeignKey  # , Table

from database import Base


class User(Base):
    __tablename__ = "user"
    __mapper_args__ = {"eager_defaults": True}
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    firstname = Column(String(63))
    lastname = Column(String(63))
    first_login = Column(sqlalchemy.types.DateTime(timezone=True))
    last_login = Column(sqlalchemy.types.DateTime(timezone=True))
    logins = Column(Integer)
    timezone = Column(String(63))
    password = Column(String(255))  # todo hash this

    def __repr__(self):
        return f"User(id={self.id!r}, username={self.username!r}, name={self.firstname!r} {self.lastname!r})"


class ApiName(str, enum.Enum):
    counter = "counter"
    spotify = "spotify"
    apple_music = "appleMusic"

    def _generate_next_value_(name, start, count, last_values):
        return name


class TokenType(str, enum.Enum):
    bearer = "bearer"
    basic = "basic"

    def _generate_next_value_(name, start, count, last_values):
        return name


class OAuth2(Base):
    __tablename__ = "oauth2"
    __mapper_args__ = {"eager_defaults": True}
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    token_type = Column(Enum(TokenType))
    api_name = Column(Enum(ApiName))
    access_token = Column(String(255))
    refresh_token = Column(String(255))
    received = Column(sqlalchemy.types.DateTime(timezone=True))
    expiry = Column(sqlalchemy.types.DateTime(timezone=True))
    last_updated = Column(sqlalchemy.types.DateTime(timezone=True),
                          default=datetime.datetime.now(datetime.timezone.utc))

    def __repr__(self):
        return f"User(id={self.id!r}, token_type={self.token_type!r}, api_name={self.api_name!r})"


class Listen(Base):
    __tablename__ = "listen"
    __mapper_args__ = {"eager_defaults": True}
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    recorded = Column(sqlalchemy.types.DateTime(timezone=True))
    api_name = Column(Enum(ApiName))
    api_id = Column(String(255))
    api_timestamp = Column(sqlalchemy.types.DateTime(timezone=True))
    duration = Column(sqlalchemy.types.Interval)
    title = Column(String(255))
    album = Column(String(255))
    artists = Column(String(1023))
    last_updated = Column(sqlalchemy.types.DateTime(timezone=True),
                          default=datetime.datetime.now(datetime.timezone.utc))

    def __init__(self, spotify_res, user_id: int):
        self.user_id = user_id
        self.recorded = datetime.datetime.now(datetime.timezone.utc)  # TODO
        self.api_name = ApiName.spotify
        self.api_id = spotify_res['item']['id']
        self.api_timestamp = datetime.datetime.fromtimestamp(spotify_res['timestamp'] / 1000, tz=timezone.utc)
        self.duration = timedelta(milliseconds=spotify_res['item']['duration_ms'])
        self.title = spotify_res['item']['name']
        self.album = spotify_res['item']['album']['name']
        if spotify_res['item']['artists'] is not None:
            self.artists = ','.join([artist['name'] for artist in spotify_res['item']['artists']])

    def likely_new_listen(self, other):
        return other is None \
               or self.user_id != other.user_id \
               or self.api_name != other.api_name \
               or (self.api_timestamp - other.api_timestamp) > datetime.timedelta(seconds=30) \
               or self.title != other.title or self.album != other.album or self.artists != other.artists
