package foodchain

import "strings"

var animals = []string{"fly", "spider", "bird", "cat", "dog", "goat", "cow", "horse"}

var remarks = []string{
	"",
	"It wriggled and jiggled and tickled inside her.",
	"How absurd to swallow a bird!",
	"Imagine that, to swallow a cat!",
	"What a hog, to swallow a dog!",
	"Just opened her throat and swallowed a goat!",
	"I don't know how she swallowed a cow!",
	"She's dead, of course!",
}

func Verse(v int) string {
	i := v - 1
	lines := []string{"I know an old lady who swallowed a " + animals[i] + "."}
	if remarks[i] != "" {
		lines = append(lines, remarks[i])
	}
	if i == len(animals)-1 {
		return strings.Join(lines, "\n")
	}
	for j := i; j > 0; j-- {
		prey := animals[j-1]
		if j == 2 {
			prey += " that wriggled and jiggled and tickled inside her"
		}
		lines = append(lines, "She swallowed the "+animals[j]+" to catch the "+prey+".")
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
	return Verses(1, len(animals))
}
