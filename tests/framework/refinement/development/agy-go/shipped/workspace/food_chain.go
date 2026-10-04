package foodchain

import (
	"strings"
)

type animal struct {
	name   string
	excl   string
	action string
}

var animals = []animal{
	{name: "fly", excl: "", action: ""},
	{name: "spider", excl: "It wriggled and jiggled and tickled inside her.", action: "that wriggled and jiggled and tickled inside her"},
	{name: "bird", excl: "How absurd to swallow a bird!", action: ""},
	{name: "cat", excl: "Imagine that, to swallow a cat!", action: ""},
	{name: "dog", excl: "What a hog, to swallow a dog!", action: ""},
	{name: "goat", excl: "Just opened her throat and swallowed a goat!", action: ""},
	{name: "cow", excl: "I don't know how she swallowed a cow!", action: ""},
	{name: "horse", excl: "She's dead, of course!", action: ""},
}

// Verse generates the v-th verse of the song (1-indexed).
func Verse(v int) string {
	if v < 1 || v > len(animals) {
		return ""
	}

	var sb strings.Builder
	curr := animals[v-1]
	sb.WriteString("I know an old lady who swallowed a ")
	sb.WriteString(curr.name)
	sb.WriteString(".\n")

	if curr.excl != "" {
		sb.WriteString(curr.excl)
		sb.WriteString("\n")
	}

	// The last animal (horse) ends immediately after the exclamation line.
	if v == len(animals) {
		return sb.String()
	}

	// Chain backwards to fly
	for i := v - 1; i > 0; i-- {
		pred := animals[i-1]
		sb.WriteString("She swallowed the ")
		sb.WriteString(animals[i].name)
		sb.WriteString(" to catch the ")
		sb.WriteString(pred.name)
		if pred.action != "" {
			sb.WriteString(" ")
			sb.WriteString(pred.action)
		}
		sb.WriteString(".\n")
	}

	sb.WriteString("I don't know why she swallowed the fly. Perhaps she'll die.\n")

	return sb.String()
}

// Verses generates the verses from start to end inclusive.
func Verses(start, end int) string {
	var verses []string
	for i := start; i <= end; i++ {
		verses = append(verses, Verse(i))
	}
	return strings.Join(verses, "\n")
}

// Song generates the entire song.
func Song() string {
	return Verses(1, len(animals))
}
