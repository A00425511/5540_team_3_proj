db.project_raw.aggregate([
  {
    $match: {
      brand: { $type: "string" },
      product_type: { $type: "string" },
      scores: { $type: "array" }
    }
  },
  {
    $project: {
      _id: 0,
      brand: 1,
      product_type: 1,
      scores: {
        $map: {
          input: { $range: [0, { $size: "$scores" }] },
          as: "i",
          in: {
            friendliness: {
              $arrayElemAt: ["$scores.friendliness", "$$i"]
            },
            price: {
              $arrayElemAt: ["$scores.price", "$$i"]
            },
            features: {
              $arrayElemAt: ["$scores.features", "$$i"]
            },
            accuracy: {
              $arrayElemAt: ["$scores.accuracy", "$$i"]
            },
            user_id: { $add: ["$$i", 1] }
          }
        }
      }
    }
  },
  {
    $out: "proj5540"
  }
]);

print("MongoDB cleaning complete.");
print("Software documents: " + db.proj5540.countDocuments({}));
