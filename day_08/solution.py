if __name__ == '__main__':
    with open("input") as f:
        img_pixels = list(f.readline().rstrip())

    # Width and height are given as part of problem input.
    img_width = 25
    img_height = 6
    pixels_per_layer = img_width * img_height

    i = 0
    layers = []
    while i < len(img_pixels):
        print(f"Reading layer {len(layers)}, offset is {i}.")

        # Must have enough pixels for another complete layer.
        assert(i + pixels_per_layer <= len(img_pixels))
        layers.append(img_pixels[i:i+pixels_per_layer])
        i += pixels_per_layer

    # We need to find the layer that contains the fewest '0' digits.
    best_index = None
    best_count = None
    for i in range(len(layers)):
        c = layers[i].count('0')

        print(f"Layer {i} has {c} zeros.")

        if best_count is None or c < best_count:
            best_index = i
            best_count = c

    print(f"Layer with fewest zeros is layer {best_index}.")

    # Now get number of '1's multiplied by number of '2's.
    layer = layers[best_index]
    print(f"The answer is {layer.count('1') * layer.count('2')}.")

    # Now we need to decode the image. 0 = black, 1 = white, and 2 = transparent.
    output = []
    for i in range(pixels_per_layer):
        p = ' '
        for layer in layers:
            v = layer[i]
            if v == '2':
                p = ' ' # transparent
            elif v == '1':
                p = '*' # white
                break
            elif v == '0':
                p = ' ' # black
                break
            else:
                raise ValueError(f"Unexpected pixel value {v}!")
        output.append(p)
    i = 0
    while i < pixels_per_layer:
        print(''.join(output[i:i+img_width]))
        i += img_width
