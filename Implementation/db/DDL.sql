CREATE TABLE "locations" (
  "id" char(36) PRIMARY KEY,
  "country" varchar,
  "city" varchar,
  "latitude" decimal,
  "longitude" decimal
);

CREATE TABLE "disasters" (
  "id" char(36) PRIMARY KEY,
  "type" varchar,
  "start_date" timestamp,
  "end_date" timestamp,
  "description" text,
  "magnitude" decimal,
  "scale" varchar,
  "radius_km" decimal
);

CREATE TABLE "impacts" (
  "disaster_id" char(36) PRIMARY KEY,
  "casualties" integer,
  "injuries" integer,
  "economic_loss" decimal,
  "area_affected_km2" decimal
);

CREATE TABLE "earthquakes" (
  "disaster_id" char(36) PRIMARY KEY,
  "depth" decimal,
  "aftershocks" integer
);

CREATE TABLE "wind_disasters" (
  "disaster_id" char(36) PRIMARY KEY,
  "pressure" decimal,
  "wind_pattern" varchar
);

CREATE TABLE "volcanic_eruptions" (
  "disaster_id" char(36) PRIMARY KEY,
  "ash_height" decimal,
  "lava_type" varchar
);

CREATE TABLE "water_disasters" (
  "disaster_id" char(36) PRIMARY KEY,
  "water_height" decimal,
  "flow_rate" decimal
);

CREATE TABLE "disaster_locations" (
  "disaster_id" char(36),
  "location_id" char(36),
  "timestamp" timestamp,
  PRIMARY KEY ("disaster_id", "location_id")
);

ALTER TABLE "impacts" ADD FOREIGN KEY ("disaster_id") REFERENCES "disasters" ("id") ON DELETE CASCADE;

ALTER TABLE "earthquakes" ADD FOREIGN KEY ("disaster_id") REFERENCES "disasters" ("id") ON DELETE CASCADE;

ALTER TABLE "wind_disasters" ADD FOREIGN KEY ("disaster_id") REFERENCES "disasters" ("id") ON DELETE CASCADE;

ALTER TABLE "volcanic_eruptions" ADD FOREIGN KEY ("disaster_id") REFERENCES "disasters" ("id") ON DELETE CASCADE;

ALTER TABLE "water_disasters" ADD FOREIGN KEY ("disaster_id") REFERENCES "disasters" ("id") ON DELETE CASCADE;

ALTER TABLE "disaster_locations" ADD FOREIGN KEY ("disaster_id") REFERENCES "disasters" ("id") ON DELETE CASCADE;

ALTER TABLE "disaster_locations" ADD FOREIGN KEY ("location_id") REFERENCES "locations" ("id") ON DELETE CASCADE;
