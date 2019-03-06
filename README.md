# Pathways

Please change database URI (e.g. username:password):

```python 
app.server.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://username:password@localhost/pathways'
```

To run the app use:

```
docker-compose -f docker-compose.yml up --build
```

The `--build` ensures that the image is rebuild from the Dockerfile.
