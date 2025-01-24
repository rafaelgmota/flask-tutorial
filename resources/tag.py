from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_jwt_extended import jwt_required

from db import db
from models import TagModel, StoreModel, ItemModel
from schemas import TagSchema, TagAndItemSchema

blp = Blueprint("Tags", "tags", description="Operations on tags")

@blp.route("/store/<int:store_id>/tag")
class TagsInStore(MethodView):
    @jwt_required()
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)

        return store.tags.all() #At store model tags is a lazy relationship, so the query need to be done (all)

    @jwt_required()
    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        # if TagModel.query.filter(TagModel.store_id == store_id, TagModel.name == tag_data["name"]).first():
        #     abort(400, message="Tag with that name already exists at store")

        tag = TagModel(**tag_data, store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except IntegrityError:
            abort(409, message="Tag already exists")
        except SQLAlchemyError as e:
            print("Error no except")
            abort(500, message=str(e))

        return tag
    
@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagsToItem(MethodView):
    @jwt_required()
    @blp.response(200, TagSchema)
    def post (self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        if item.store.id != tag.store.id:
            abort(400, message="Make sure item and tag belongs to same store before linking")

        item.tags.append(tag) #This, with add and commit above, do all the magic using the secondary table

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, "Some error accurred")

        return tag
    
    @jwt_required()
    @blp.response(200, TagAndItemSchema)
    def delete (self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag) #This, with add and commit above, do all the magic using the secondary table

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, "Some error accurred")

        return {"message": "Tag removed from item", "item": item, "tag": tag}
    
@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @jwt_required()
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag
    
    @jwt_required()
    @blp.response(202, description="Deletes a tag if no item is tagged with it")
    @blp.alt_response(404, description="Tag not found")
    @blp.alt_response(400, description="Returned if the tag is assigned to one or more item. In this case, the tag is not deleted")
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.items: #Verify if there is some item with this tag
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted."}
        
        abort(400, message="Could not delete Tag. Make sure tag is not associated with any item")

