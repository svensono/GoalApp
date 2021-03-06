from abc import ABCMeta, abstractmethod
from contextlib import contextmanager

from sqlalchemy import create_engine, MetaData
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import scoped_session, sessionmaker


class ORM(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, driver, user, password, host, port, database):
        raise NotImplementedError

    @abstractmethod
    def session(self):
        raise NotImplementedError

    @abstractmethod
    def unit_of_work(self):
        raise NotImplementedError


class SqlAlchemy(ORM):

    def __init__(self, driver, user, password, host, port, database):
        self.engine = create_engine(
            f"{driver}://{user}:{password}@{host}:{port}/{database}")
        self.session_factory = scoped_session(sessionmaker(self.engine), )
        self.metadata = MetaData(self.engine)

    def session(self):
        return self.session_factory()

    @contextmanager
    def unit_of_work(self):
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            session.close()
