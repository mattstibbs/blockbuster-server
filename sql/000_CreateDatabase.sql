-- Create the role for blockbuster login ---
CREATE USER blockbuster WITH PASSWORD 'blockbuster';

--- Create the blockbuster database ---
CREATE DATABASE blockbuster OWNER blockbuster;

