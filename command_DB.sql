BEGIN;
--
-- Create model Product
--
CREATE TABLE "main_product" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(32) NOT NULL, "description" text NOT NULL, "price" decimal NOT NULL, "slug" varchar(48) NOT NULL, "active" bool NOT NULL, "in_stock" bool NOT NULL, "date_updated" datetime NOT NULL);
CREATE INDEX "main_product_slug_85058272" ON "main_product" ("slug");
COMMIT;
