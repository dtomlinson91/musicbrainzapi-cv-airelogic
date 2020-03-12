# Some python

## Some test python

!!! warning "Important warning"
    This isn't yet complete.

```python
def _generate_word_cloud(self) -> None:
    """Generates a word cloud
    """
    self.wc = WordCloud(
        max_words=150,
        width=1500,
        height=1500,
        mask=self.char_mask,
        random_state=1,
    ).generate_from_frequencies(self.freq)
    return self
```
