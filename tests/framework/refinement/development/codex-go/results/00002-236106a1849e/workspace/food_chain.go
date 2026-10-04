package foodchain

import "strings"

func Verse(v int) string {
	animals := []string{"fly", "spider", "bird", "cat", "dog", "goat", "cow", "horse"}
	remarks := []string{
		"",
		"It wriggled and jiggled and tickled inside her.",
		"How absurd to swallow a bird!",
		"Imagine that, to swallow a cat!",
		"What a hog, to swallow a dog!",
		"Just opened her throat and swallowed a goat!",
		"I don't know how she swallowed a cow!",
		"She's dead, of course!",
	}
	lines := []string{"I know an old lady who swallowed a " + animals[v-1] + "."}
	if remarks[v-1] != "" {
		lines = append(lines, remarks[v-1])
	}
	if v == 8 {
		return strings.Join(lines, "\n")
	}
	for i := v - 1; i > 0; i-- {
		line := "She swallowed the " + animals[i] + " to catch the " + animals[i-1]
		if i == 2 {
			line += " that wriggled and jiggled and tickled inside her"
		}
		lines = append(lines, line+".")
	}
	lines = append(lines, "I don't know why she swallowed the fly. Perhaps she'll die.")
	return strings.Join(lines, "\n")
}

func Verses(start, end int) string {
	var verses []string
	for v := start; v <= end; v++ {
		verses = append(verses, Verse(v))
	}
	return strings.Join(verses, "\n\n")
}

func Song() string {
	return Verses(1, 8)
}
