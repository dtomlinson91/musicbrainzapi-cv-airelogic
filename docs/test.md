# musicbrainzapi.wordcloud package

Wordcloud from lyrics.


### class musicbrainzapi.wordcloud.LyricsWordcloud(pillow_img: PIL.PngImagePlugin.PngImageFile, all_albums_lyrics_count: Lyrics.all_albums_lyrics_count)
Bases: `object`

Create a word cloud from Lyrics.


* **Variables**


    * **all_albums_lyrics_count** (*list*) – List of all albums + track lyrics counted by each word


    * **char_mask** (*np.array*) – numpy array containing data for the word cloud image


    * **freq** (*collections.Counter*) – Counter object containing counts for all words across all tracks


    * **lyrics_list** (*list*) – List of all words from all lyrics across all tracks.


    * **pillow_img** (*PIL.PngImagePlugin.PngImageFile*) – pillow image of the word cloud base


    * **wc** (*wordcloud.WordCloud*) – WordCloud object



#### \__init__(pillow_img: PIL.PngImagePlugin.PngImageFile, all_albums_lyrics_count: Lyrics.all_albums_lyrics_count)
Create a worcloud object.


* **Parameters**


    * **pillow_img** (*PIL.PngImagePlugin.PngImageFile*) – pillow image of the word cloud base


    * **all_albums_lyrics_count** (*Lyrics.all_albums_lyrics_count*) – List of all albums + track lyrics counted by each word



#### classmethod use_microphone(all_albums_lyrics_count: Lyrics.all_albums_lyrics_count)
Class method to instantiate with a microphone base image.


* **Parameters**

    **all_albums_lyrics_count** (*Lyrics.all_albums_lyrics_count*) – List of all albums + track lyrics counted by each word



#### static generate_grey_colours(\*args, \*\*kwargs)
Static method to generate a random grey colour.


#### _get_lyrics_list()
Gets all words from lyrics in a single list + cleans them.


#### _get_frequencies()
Get frequencies of words from a list.


#### _get_char_mask()
Gets a numpy array for the image file.


#### _generate_word_cloud()
Generates a word cloud


#### _generate_plot()
Plots the wordcloud and sets matplotlib options.


#### create_word_cloud()
Creates a word cloud
