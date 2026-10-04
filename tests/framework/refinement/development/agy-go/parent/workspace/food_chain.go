package foodchain

import "strings"

type animal struct {
	name   string
	excl   string
	action string
}

var animals = []animal{
	{"fly", "", ""},
	{"spider", "It wriggled and jiggled and tickled inside her.\n", " that wriggled and jiggled and tickled inside her"},
	{"bird", "How absurd to swallow a bird!\n", ""},
	{"cat", "Imagine that, to swallow a cat!\n", ""},
	{"dog", "What a hog, to swallow a dog!\n", ""},
	{"goat", "Just opened her throat and swallowed a goat!\n", ""},
	{"cow", "I don't know how she swallowed a cow!\n", ""},
	{"horse", "She's dead, of course!", ""},
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

	if animals[idx].excl != "" {
		sb.WriteString(animals[idx].excl)
	}

	if animals[idx].name == "horse" {
		return sb.String()
	}

	for i := idx; i > 0; i-- {
		sb.WriteString("She swallowed the ")
		sb.WriteString(animals[i].name)
		sb.WriteString(" to catch the ")
		sb.WriteString(animals[i-1].name)
		sb.WriteString(animals[i-1].action)
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
