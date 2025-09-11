from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
import model
import orm
import repository
import services


orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)
app.debug = True


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    line = model.OrderLine(
        request.json["orderid"],
        request.json["sku"],
        request.json["qty"],
    )

    try:
        batchref = services.allocate(line, repo, session)
    except (model.OutOfStock, services.InvalidSku) as e:
        return {"message": str(e)}, 400

    return {"batchref": batchref}, 201


@app.route("/deallocate", methods=["POST"])
def deallocate_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    try:
        batchref = services.deallocate(
            request.json["orderid"], request.json["sku"], repo, session
        )
    except services.InvalidSku as e:
        return {"message": str(e)}, 400
    return {"batchref": batchref}, 201


@app.route("/batches", methods=["POST"])
def add_batch_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    batch = model.Batch(
        request.json["batchref"],
        request.json["sku"],
        request.json["qty"],
        request.json["eta"],
    )
    try:
        services.add_batch(batch=batch, repo=repo, session=session)
    except Exception as e:
        return {"message": str(e)}, 400

    return {"batchref": batch.reference}, 201
