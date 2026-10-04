package foodchain

import (
	"fmt"
	"strings"
)

type animal struct {
	name   string
	excl   string
	action string
}

var animals = []animal{
	{name: "fly"},
	{name: "spider", excl: "It wriggled and jiggled and tickled inside her.", action: " that wriggled and jiggled and tickled inside her"},
	{name: "bird", excl: "How absurd to swallow a bird!"},
	{name: "cat", excl: "Imagine that, to swallow a cat!"},
	{name: "dog", excl: "What a hog, to swallow a dog!"},
	{name: "goat", excl: "Just opened her throat and swallowed a goat!"},
	{name: "cow", excl: "I don't know how she swallowed a cow!"},
	{name: "horse", excl: "She's dead, of course!"},
}

// Verse generates a single verse (1-indexed) of the song.
func Verse(v int) string {
	if v < 1 || v > len(animals) {
		return ""
	}

	idx := v - 1
	var lines []string
	lines = append(lines, fmt.Sprintf("I know an old lady who swallowed a %s.", animals[idx].name))

	if animals[idx].excl != "" {
		lines = append(lines, animals[idx].excl)
	}

	// For the last animal (horse), it terminates immediately after the exclamation.
	if v == len(animals) {
		return strings.Join(lines, "\n")
	}

	for i := idx; i > 0; i-- {
		prev := animals[i-1]
		lines = append(lines, fmt.Sprintf("She swallowed the %s to catch the %s%s.", animals[i].name, prev.name, prev.action))
	}

	lines = append(lines, "I don't know why she swallowed the fly. Perhaps she'll die.")

	return strings.Join(lines, "\n")
}

// Verses generates verses from start to end (inclusive), separated by a blank line.
func Verses(start, end int) string {
	var verses []string
	for i := start; i <= end; i++ {
		verses = append(verses, Verse(i))
	}
	return strings.Join(verses, "\n\n")
}

// Song generates the entire song.
func Song() string {
	return Verses(1, len(animals))
}
