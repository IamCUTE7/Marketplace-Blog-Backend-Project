from marketplace_blog.repositories.categories import CategoryRepository


class CategoryService:
    def __init__(self, db):
        self.category_repo = CategoryRepository(db)

    async def get_category_by_id(self, category_id):
        return await self.category_repo.get_category_by_id(category_id)

    async def get_categories(self):
        return await self.category_repo.get_categories()

    async def create_category(self, body):
        return await self.category_repo.create_category(body.name)

    async def update_category(self, category_id, **kwargs):
        return await self.category_repo.update_category(category_id, **kwargs)

    async def delete_category(self, category_id):
        return await self.category_repo.delete_category(category_id)
