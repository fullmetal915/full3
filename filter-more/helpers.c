#include "helpers.h"

// roundoff value
uint8_t roundoff (float value)
{
    if (value- (int)value < 0.5)
    {
        value = (int)value;
    }
    else if(value- (int)value >= 0.5)
    {
        value += 1;
    }
    return (uint8_t)value;
}

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            float avg = ((float)image[i][j].rgbtRed + (float)image[i][j].rgbtBlue + (float)image[i][j].rgbtGreen) / 3;
            if (floor(avg) != ceil(avg))
            {
                avg = round(avg);
            }
            image[i][j].rgbtRed = avg;
            image[i][j].rgbtBlue = avg;
            image[i][j].rgbtGreen = avg;
        }
    }
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < ceil(width / 2); j++)
        {
            {
                RGBTRIPLE temp = image[i][(width - 1) - j];
                image[i][(width - 1) - j] = image[i][j];
                image[i][j] = temp;
            }
        }
    }
    return;
}

// Blur image  (i = 0 && j = (width - 1)) || (i = (height - 1) && j = (width - 1))
void blur(int height, int width, RGBTRIPLE (image[height][width]))
{
    RGBTRIPLE temp[height][width];
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            temp[i][j] = image[i][j];
        }
    }
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int tempr = 0, tempb = 0, tempg = 0, count = 0;
            for (int r = -1; r < 2; r++)
            {
                for (int c = -1; c < 2; c++)
                {
                    if ((i + r < 0) ||(i + r > (height - 1)))
                    {
                        continue;
                    }
                    else if ((j + c < 0) || (j + c > (width - 1)))
                    {
                        continue;
                    }
                    tempr += temp[i + r][j + c].rgbtRed;
                    tempb += temp[i + r][j + c].rgbtBlue;
                    tempg += temp[i + r][j + c].rgbtGreen;
                    count += 1;
                }
            }
        image[i][j].rgbtRed = round((float)tempr / count);
        image[i][j].rgbtBlue = round((float)tempb / count);
        image[i][j].rgbtGreen = round((float)tempg / count);
        }
    }
    return;
}

// Detect edges
void edges(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE temp[height][width];
    int Gx[3][3] = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};
    int Gy[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            temp[i][j] = image[i][j];
        }
    }
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int GxBlue = 0, GyBlue = 0;
            int GxGreen = 0, GyGreen = 0;
            int GxRed = 0, GyRed = 0;
            for (int r = -1; r < 2; r++)
            {
                for (int c = -1; c < 2; c++)
                {
                    if (((i + r) < 0 || (i + r) > (height - 1)) || ((j + c) < 0 || (j + c) >(width - 1)))
                    {
                        continue;
                    }
                    GxBlue += temp[i + r][j + c].rgbtBlue * Gx[r + 1][c + 1];
                    GyBlue += temp[i + r][j + c].rgbtBlue * Gy[r + 1][c + 1];
                    GxGreen += temp[i + r][j + c].rgbtGreen * Gx[r + 1][c + 1];
                    GyGreen += temp[i + r][j + c].rgbtGreen * Gy[r + 1][c + 1];
                    GxRed += temp[i + r][j + c].rgbtRed * Gx[r + 1][c + 1];
                    GyRed += temp[i + r][j + c]. rgbtRed * Gy[r + 1][c + 1];
                }
            }
        image[i][j].rgbtBlue = sqrt((GxBlue * GxBlue) + (GyBlue * GyBlue)) > 255 ? 255 : roundoff(sqrt((GxBlue * GxBlue) + (GyBlue * GyBlue)));
        image[i][j].rgbtGreen = sqrt((GxGreen * GxGreen) + (GyGreen * GyGreen)) > 255 ? 255 : roundoff(sqrt((GxGreen * GxGreen) + (GyGreen * GyGreen)));
        image[i][j].rgbtRed = sqrt((GxRed * GxRed) + (GyRed * GyRed)) > 255 ? 255 : roundoff(sqrt((GxRed * GxRed) + (GyRed * GyRed)));
        }
    }
    return;
}
