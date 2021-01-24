from os import path
import sys
import subprocess
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import typer


Base = declarative_base()
engine = create_engine('sqlite:///jump.db')
Session = sessionmaker(bind=engine)
session = Session()
app = typer.Typer()


class Host(Base):
    __tablename__ = 'hosts'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    user = Column(String)

    def __repr__(self):
        return f'{self.name}'


@app.command()
def add_host(hostname: str, user: str):
    typer.echo(f'Hostname: {user}@{hostname}')
    host = Host(name=hostname, user=user)
    session.add(host)
    session.commit()


@app.command()
def list_hosts():
    typer.echo('Listing all hosts...')
    for host in session.query(Host).order_by(Host.name):
        print(f'{host.id} => {host.user}@{host.name}')

@app.command()
def del_host(host_id: int):
    row = session.query(Host).get(host_id)
    typer.echo(f'Deleting host: {row.name}')
    session.delete(row)
    session.commit()

@app.command()
def edit_host(
    host_id: str,
    hostname: str = typer.Option("", help="Hostname to change"),
    username: str = typer.Option("", help="Username to login in as")
):
    row = session.query(Host).get(host_id)

    if not row:
        typer.echo("Unknown error")
        sys.exit(1)

    if not hostname and not username:
        typer.echo("Nothing to change")
        sys.exit(1)

    if hostname:
        row.name = hostname

    if username:
        row.user = username

    session.commit()



@app.command()
def connect(name: str):
    row = session.query(Host).filter_by(name=name).first()
    if not row:
        typer.echo(f'Host not found: {name}')
        sys.exit(1)
    subprocess.run(['ssh', f'{row.user}@{row.name}'])


def check_db_exists():
    result = False

    return path.exists('./jump.db')


if __name__ == '__main__':
    if not check_db_exists():
        Base.metadata.create_all(engine)
    app()