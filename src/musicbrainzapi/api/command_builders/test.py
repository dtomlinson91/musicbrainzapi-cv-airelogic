import musicbrainzngs
from musicbrainzapi import __header__, __version__
import addict

from pprint import pprint


def main():
    musicbrainzngs.set_useragent(
        __header__.__header__, __version__.__version__
    )
    resp_0 = musicbrainzngs.browse_release_groups(
        # artist='1a425bbd-cca4-4b2c-aeb7-71cb176c828a',
        artist='0383dadf-2a4e-4d10-a46a-e9e041da8eb3',
        release_type=['album'],
        limit=100,
    )
    # pprint(resp_0)
    resp_0 = addict.Dict(resp_0)

    release_group_ids = addict.Dict()
    album_info = addict.Dict()

    release_group_ids = addict.Dict(
        (i.id, i.title)
        for i in resp_0['release-group-list']
        if i.type == 'Album'
    )

    all_albums = list()

    pprint(release_group_ids)

    pprint(len(release_group_ids))

    for id, alb in release_group_ids.items():
        # print(id, alb)

        resp_1 = addict.Dict(
            musicbrainzngs.browse_releases(
                release_group=id,
                release_type=['album'],
                includes=['recordings'],
                limit=100,
            )
        )

        album_track_count = [
            i['medium-list'][0]['track-count'] for i in resp_1['release-list']
        ]

        max_track_pos = album_track_count.index(max(album_track_count))

        # print(max_track_pos)

        # print(album_track_count)

        album_tracks = resp_1['release-list'][max_track_pos]

        album_year = resp_1['release-list'][max_track_pos].date.split('-')[0]

        album_tracks = addict.Dict(
            (
                alb + f' [{album_year}]',
                [
                    i.recording.title
                    for i in resp_1['release-list'][max_track_pos][
                        'medium-list'
                    ][0]['track-list']
                ],
            )
        )

        # pprint(resp_1['release-list'][3])
        # print(max_track_pos)
        # pprint(album_tracks)

        all_albums.append(album_tracks)

    pprint(all_albums)
    raise (SystemExit)

    # pprint(album_info)

    # resp_1 = addict.Dict(
    #     musicbrainzngs.browse_releases(
    #         release_group='1174aa3d-1c9e-4745-be8d-e21a61b1a22d',
    #         release_type=['album'],
    #         includes=['recordings'],
    #         limit=100,
    #     )
    # )

    # resp_1 = addict.Dict(resp_1)

    # pprint(resp_1)

    # print(resp_1['release-list'][0]['medium-list'][0]['track-count'])

    # album_track_count = [
    #     i['medium-list'][0]['track-count'] for i in resp_1['release-list']
    # ]

    # max_track_count = print(max(album_track_count))

    # album = addict.Dict(())


if __name__ == '__main__':
    main()
