package foodchain

import (
	"fmt"
	"strings"
)

type animal struct {
	name   string
	remark string
}

var animals = []animal{
	{"fly", ""},
	{"spider", "It wriggled and jiggled and tickled inside her."},
	{"bird", "How absurd to swallow a bird!"},
	{"cat", "Imagine that, to swallow a cat!"},
	{"dog", "What a hog, to swallow a dog!"},
	{"goat", "Just opened her throat and swallowed a goat!"},
	{"cow", "I don't know how she swallowed a cow!"},
	{"horse", "She's dead, of course!"},
}

func Verse(v int) string {
	if v < 1 || v > len(animals) {
		return ""
	}

	idx := v - 1
	var lines []string

	lines = append(lines, fmt.Sprintf("I know an old lady who swallowed a %s.", animals[idx].name))

	if animals[idx].remark != "" {
		lines = append(lines, animals[idx].remark)
	}

	if idx == len(animals)-1 {
		return strings.Join(lines, "\n")
	}

	for j := idx; j > 0; j-- {
		prev := animals[j-1].name
		if prev == "spider" {
			lines = append(lines, fmt.Sprintf("She swallowed the %s to catch the spider that wriggled and jiggled and tickled inside her.", animals[j].name))
		} else {
			lines = append(lines, fmt.Sprintf("She swallowed the %s to catch the %s.", animals[j].name, prev))
		}
	}

	lines = append(lines, "I don't know why she swallowed the fly. Perhaps she'll die.")

	return strings.Join(lines, "\n")
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
