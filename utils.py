from collections import defaultdict


def generate_stats(memes):
    if len(memes) == 0:
        return {
            "No memes":
            "Try increasing the duration or posting some memes to change this ;)"
        }
    top_3_memes = sorted(memes, key=lambda m: m['upvotes'], reverse=True)[:3]
    top_3_memes = [
        f"<https://memes.party/?meme={m['id']}> {m['meme_score']}"
        for m in top_3_memes
    ]
    poaster_scores = defaultdict(int)
    poaster_meme_counts = defaultdict(int)
    upvotes_casted = 0

    for m in memes:
        poaster_scores[m['poaster']['username']] += m['meme_score']
        poaster_meme_counts[m['poaster']['username']] += 1
        upvotes_casted += m['upvotes']

    poaster_scores = [(p, s) for p, s in poaster_scores.items()]
    poaster_counts = [(p, c) for p, c in poaster_meme_counts.items()]

    most_prolific_poaster = max(poaster_counts, key=lambda x: x[1])

    def get_profile(username):
        return f"<https://memes.party/profile/{username}>"

    most_voted_memelords = sorted(poaster_scores,
                                  key=lambda x: x[1],
                                  reverse=True)[:3]
    most_voted_memelords = [
        f'{get_profile(m[0])} {m[1]} points' for m in most_voted_memelords
    ]

    return {
        "Total Memes":
        len(memes),
        "Active Registered Poasters":
        len(set(m['poaster']['username'] for m in memes)),
        "Most Prolific MemeLord":
        f'{get_profile(most_prolific_poaster[0])} {most_prolific_poaster[1]} memes',
        "Most Voted MemeLords":
        most_voted_memelords,
        "Most Voted Memes":
        top_3_memes
    }


def list_to_tab_str(l):
    if type(l) is not list:
        return l
    return "".join(f'\n\t{v}' for v in l)


def discord_print_dict(d):
    return '\n'.join(f'**{k}**: {list_to_tab_str(v)}' for k, v in d.items())
