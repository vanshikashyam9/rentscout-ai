from area_recommender import recommend_areas

results = recommend_areas(1800)

print("\n🏠 BEST AREAS:\n")

for area in results:
    print(area)