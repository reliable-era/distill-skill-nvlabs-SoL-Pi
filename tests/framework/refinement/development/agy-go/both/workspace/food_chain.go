package foodchain

import (
	"fmt"
	"strings"
)

type animalInfo struct {
	name   string
	custom string
}

var animals = []animalInfo{
	{"fly", ""},
	{"spider", "It wriggled and jiggled and tickled inside her.\n"},
	{"bird", "How absurd to swallow a bird!\n"},
	{"cat", "Imagine that, to swallow a cat!\n"},
	{"dog", "What a hog, to swallow a dog!\n"},
	{"goat", "Just opened her throat and swallowed a goat!\n"},
	{"cow", "I don't know how she swallowed a cow!\n"},
	{"horse", "She's dead, of course!"},
}

func Verse(v int) string {
	if v < 1 || v > len(animals) {
		return ""
	}

	idx := v - 1
	var sb strings.Builder
	sb.WriteString(fmt.Sprintf("I know an old lady who swallowed a %s.\n", animals[idx].name))

	if animals[idx].custom != "" {
		sb.WriteString(animals[idx].custom)
	}

	if idx == len(animals)-1 {
		return sb.String()
	}

	for i := idx; i > 0; i-- {
		swallowed := animals[i].name
		target := animals[i-1].name
		if target == "spider" {
			sb.WriteString(fmt.Sprintf("She swallowed the %s to catch the spider that wriggled and jiggled and tickled inside her.\n", swallowed))
		} else {
			sb.WriteString(fmt.Sprintf("She swallowed the %s to catch the %s.\n", swallowed, target))
		}
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
