def recommend_professions_top5(
    student_id,
    df_clustered,
    interests,
    career_islands,
    cluster_to_islands,
    interest_to_islands,
    interest_keywords,
    index_to_islands,
    profession_to_topics,
    interest_island_weights,
    top_n=5
):
    cluster = df_clustered.loc[df_clustered["ID"] == student_id, "cluster"].values[0]
    cluster_islands = cluster_to_islands.get(cluster, [])

    island_scores = {}

    for interest in interests:
        for island, w in interest_island_weights.get(interest, {}).items():
            island_scores[island] = island_scores.get(island, 0) + w

    final_islands = list(dict.fromkeys(cluster_islands + list(island_scores.keys())))

    final_islands = [i for i in final_islands if island_scores.get(i, 0) > 0]

    final_islands = sorted(final_islands, key=lambda x: island_scores.get(x, 0), reverse=True)

    island_to_professions = {}
    for island in final_islands:
        profs = career_islands.get(island, {}).get("directions", {})
        all_profs = []
        for direction, prof_list in profs.items():
            all_profs.extend(prof_list)
        island_to_professions[island] = list(set(all_profs))

    def score_profession(prof, island):
        score = 0

        topics = profession_to_topics.get(prof, [])
        topics_str = " ".join(topics).lower()

        for interest in interests:
            for kw in interest_keywords.get(interest.lower(), []):
                if kw.lower() in topics_str:
                    score += 3

        prof_lower = prof.lower()
        for interest in interests:
            for kw in interest_keywords.get(interest.lower(), []):
                if kw.lower() in prof_lower:
                    score += 1

        score += island_scores.get(island, 0)

        return score

    result = {}
    for island in final_islands[:3]:  # ← ТОП‑3 острова
        profs = island_to_professions[island]
        scored = sorted(profs, key=lambda p: score_profession(p, island), reverse=True)

        result[island] = {
            "weight": island_scores.get(island, 0),
            "professions": scored[:top_n]
        }

    return result


def pretty_format(recs):
    text = "🎯 *Твои персональные рекомендации*\n\n"

    for island, data in recs.items():
        text += f"🏝️ *{island.upper()}* — приоритет {data['weight']}\n"
        text += "```\n"
        for p in data["professions"]:
            text += f"• {p}\n"
        text += "```\n\n"

    return text


