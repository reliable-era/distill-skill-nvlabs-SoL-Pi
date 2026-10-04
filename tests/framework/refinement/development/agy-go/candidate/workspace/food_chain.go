package foodchain

import "strings"

type animalInfo struct {
	name    string
	comment string
}

var animals = []animalInfo{
	{name: "fly", comment: ""},
	{name: "spider", comment: "It wriggled and jiggled and tickled inside her.\n"},
	{name: "bird", comment: "How absurd to swallow a bird!\n"},
	{name: "cat", comment: "Imagine that, to swallow a cat!\n"},
	{name: "dog", comment: "What a hog, to swallow a dog!\n"},
	{name: "goat", comment: "Just opened her throat and swallowed a goat!\n"},
	{name: "cow", comment: "I don't know how she swallowed a cow!\n"},
	{name: "horse", comment: "She's dead, of course!"},
}

func Verse(v int) string {
	if v < 1 || v > len(animals) {
		return ""
	}

	idx := v - 1
	var sb strings.Builder

	sb.WriteString("I know an old lady who swallowed a ")
	sb.WriteString(animals[idx].name)
	sb.WriteString(".\n")

	if animals[idx].comment != "" {
		sb.WriteString(animals[idx].comment)
	}

	if v == len(animals) {
		return sb.String()
	}

	for i := idx; i > 0; i-- {
		sb.WriteString("She swallowed the ")
		sb.WriteString(animals[i].name)
		sb.WriteString(" to catch the ")
		sb.WriteString(animals[i-1].name)
		if animals[i-1].name == "spider" {
			sb.WriteString(" that wriggled and jiggled and tickled inside her")
		}
		sb.WriteString(".\n")
	}

	sb.WriteString("I don't know why she swallowed the fly. Perhaps she'll die.")

	return sb.String()
}

func Verses(start, end int) string {
	var verses []string
	for i := start; i <= end; i++ {
		verses = append(verses, Verse(i))
	}
	return strings.Join(verses, "\n\n")
}

func Song() string {
	return Verses(1, len(animals))
}
